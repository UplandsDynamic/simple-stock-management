/* react */
import React, {Component} from 'react';
import ReactDOM from 'react-dom';
/* environment settings */
import Env from './env.jsx';
/* app components */
import LoginForm from './loginform.jsx';
import DataTable from './data-table.jsx';
import StockUpdateModal from './stock-update-modal.jsx';
import ApiRequest from './api-request.jsx';
import Message from './message.jsx';
import Footer from './footer.jsx';
/* cookies */
import Cookies from 'js-cookie';

/* css */
import '../css/index.css';
/* font awesome icons */
import {library} from '@fortawesome/fontawesome-svg-core'
import {faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit);
/* axios */
import axios from 'axios/index';

axios.defaults.withCredentials = true;

/* App root */
class App extends React.Component {

    static APP_DETAILS = Env().appDetails;

    static API_OPTIONS =
        {
            /* used to define available API options in the api-request component */
            GET_STOCK: {method: 'GET', desc: 'request to get stock data'},
            PATCH_STOCK: {method: 'PATCH', desc: 'PATCH request to update stock data'},
            ADD_STOCK: {method: 'POST', desc: 'POST request to add stock data'},
            DELETE_STOCK_LINE: {method: 'DELETE', desc: 'DELETE request to delete stock line'},
            POST_AUTH: {method: 'POST', desc: 'POST request to for authorization'},
            PATCH_CHANGE_PW: {method: 'PATCH', desc: 'PATCH request to for changing password'},
        };

    static defaultStockRecordData = () => {
        return {data: {results: []}}
    };

    static defaultStockRecordMeta = () => {
        return {
            page: 1,
            limit: 25,
            pagerMainSize: 5,
            pagerEndSize: 3,
            orderBy: 'sku',
            orderDir: '-',
            preserveOrder: false,
            cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
            url: null,
            userIsAdmin: false,
            search: ''
        }
    };

    static defaultStockUpdateData = () => {
        return {
            units_total: 0,
            unit_price: 0.00,
            desc: '',
            sku: ''
        }
    };

    static defaultStockUpdateMeta = () => {
        return {
            cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
            url: null,
            userIsAdmin: false,
            newRecord: false,
            deleteRecord: false,
        }
    };

    static defaultAuthMeta = () => {
        return {
            url: `${Env().apiRoot}/api-token-auth/`,
            change_pw_url: `${Env().apiRoot}/v1/change-password/`,
            authenticated: Boolean(sessionStorage.getItem('apiToken')),
            cacheControl: 'no-cache',
            requestData: null,
        }
    };


    // constructor fires before component mounted
    constructor(props) {
        super(props); // makes 'this' refer to component (i.e. like python self)
        // set local state
        this.state = {
            // only initialise stockData with required defaults for 1st request and
            // BEFORE data returned. Rest all added in call to stockDataHandler called after response received
            stockRecordData: App.defaultStockRecordData(),
            stockRecordMeta: App.defaultStockRecordMeta(),
            stockUpdateData: App.defaultStockUpdateData(),
            stockUpdateMeta: App.defaultStockUpdateMeta(),
            authMeta: App.defaultAuthMeta(),
            stockUpdateModalOpen: false,
            apiTrigger: null,  // will be one of API_OPTIONS when triggered
            message: null,
            messageClass: '',
            greeting: App.APP_DETAILS.greeting,
            csrfToken: this.getCSRFToken()
        };
    }

    getCSRFToken = () => {
        return Cookies.get('csrftoken')
    };

    setSessionStorage = ({key, value}) => {
        sessionStorage.setItem(key, value);
    };

    getSessionStorage = (key) => {
        //return JSON.parse(localStorage.getItem(key));
        return sessionStorage.getItem(key);
    };

    deleteSessionStorage = (keys = []) => {
        if (keys.length > 0) {
            keys.forEach((k) => {
                sessionStorage.removeItem(k)
            })
        }
        return true;
    };


    authenticate = ({apiTrigger = null, requestData = null, auth = false} = {}) => {
        // ensure token deleted if auth false
        !auth ? this.deleteSessionStorage(['apiToken', 'username']) : null;
        // triggers API to get auth token
        this.setState({
            apiTrigger: apiTrigger,
            authMeta: {
                url: this.state.authMeta.url,
                change_pw_url: this.state.authMeta.change_pw_url,
                authenticated: auth,
                requestData: requestData
            }
        })
    };

    resetUpdateDataState = () => {
        this.setState({
            stockUpdateData: App.defaultStockUpdateData(),
            stockUpdateMeta: App.defaultStockUpdateMeta(),
        })
    };

    setStockRecordState = ({stockRecord, updatedData, apiTrigger = null} = {}) => {
        /*
        method to update state for record being retrieved (GET request)
         */
        let metaState = this.state.stockRecordMeta;
        let recordState = stockRecord && stockRecord.data ? stockRecord.data : this.state.stockRecordData;
        //let metaState = this.state.stockRecordMeta;
        // record response data
        if (updatedData) {  // update just fields of the record being updated
            Object.entries(recordState.data.results).forEach((r, index) => {
                if (r[1]['id'] === updatedData['id']) {
                    recordState['data']['results'][index] = updatedData
                }
            });
            metaState['datetime_of_request'] = updatedData['datetime_of_request'];
            metaState['userIsAdmin'] = updatedData['user_is_admin'];
            this.setMessage({message: 'Record updated!', messageClass: 'alert alert-success'})
        }
        if (stockRecord) {
            /*update record request meta (sets new request URLs, etc) */
            Object.entries(stockRecord.meta ? stockRecord.meta : metaState).forEach((kvArray) => {
                metaState[kvArray[0]] = kvArray[1];
            });
            if (recordState['data']['results'].length) {
                // add time of request from recordState to metaState
                metaState['datetime_of_request'] = recordState['data']['results'][0]['datetime_of_request'];
                // add user admin status from recordState to metaState
                metaState['userIsAdmin'] = recordState['data']['results'][0]['user_is_admin'];
            }
        }
        // ensure page never falls below 1!
        metaState.page < 1 ? metaState.page = 1 : metaState.page;
        // set new state, then once done (as callback) reset state data to defaults
        this.setState({
            stockRecordData: recordState, stockRecordMeta: metaState,
            apiTrigger: apiTrigger,
        }, this.resetUpdateDataState());
    };

    setStockUpdateRecordState = ({record = null, apiTrigger = null, clearData = false} = {}) => {
        /*
        method to update the state for the record being edited (PATCH request), or add
        new record
         */
        clearData ? this.setState({stockUpdateData: App.defaultStockUpdateData()}) : null;  // clear updateData if requested
        let recordState = this.state.stockUpdateData;
        let metaState = this.state.stockUpdateMeta;
        let admin = false;
        Object.entries(record && record.data ? record.data : recordState).forEach((kvArray) => {
            /*add data to record (removing unnecessary elements & assigning
            user admin status to stockUpdateMeta instead */
            kvArray[0] === 'user_is_admin' ? admin = kvArray[1] : null;
            recordState[kvArray[0]] = kvArray[1];
        });
        Object.entries(record && record.meta ? record.meta : metaState).forEach((kvArray) => {
            // add new meta to record
            metaState[kvArray[0]] = kvArray[1];
        });
        metaState['userIsAdmin'] = admin;
        this.setState({
            stockUpdateMeta: metaState,
            stockUpdateData: recordState,
            apiTrigger: apiTrigger
        });
    };


    openStockUpdateModalHandler = ({record = this.state.stockUpdateData} = {}) => {
        /*
        method to open the stock addition/update modal & send incoming record-to-be-updated
        to the setStockUpdateRecordState method (to update the state!)
         */
        this.setStockUpdateRecordState({record: record});
        this.setStockUpdateModalState({state: true});
    };

    setStockUpdateModalState = ({state = false, actionCancelled = false} = {}) => {
        /*
        method to update the state for the modal open/close state and
         if action was cancelled, RESET stockUpdateData & stockUpdateMeta to default values
         */
        this.setState({stockUpdateModalOpen: state});
        actionCancelled ? this.resetUpdateDataState() : null;
    };

    disarmAPI = () => {
        // disables API active state
        this.setState({apiTrigger: null})
    };

    setMessage = ({message = null, messageClass = ''} = {}) => {
        this.setState({message: message, messageClass: messageClass});
    };

    render() {
        let dataTable;
        if (this.state.authMeta.authenticated) {
            dataTable = (
                <DataTable stockRecordData={this.state.stockRecordData}
                           stockRecordMeta={this.state.stockRecordMeta}
                           message={this.state.message}
                           messageClass={this.state.messageClass}
                           API_OPTIONS={App.API_OPTIONS}
                           APP_DETAILS={App.APP_DETAILS}
                           setStockRecordState={this.setStockRecordState}
                           openStockUpdateModalHandler={this.openStockUpdateModalHandler}
                           setMessage={this.setMessage}
                />
            )
        }
        return (
            <div className={'app-main'}>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className={'col-12'}>
                            <LoginForm authenticated={this.state.authenticated}
                                       API_OPTIONS={App.API_OPTIONS}
                                       authMeta={this.state.authMeta}
                                       greeting={App.APP_DETAILS.greeting}
                                       getSessionStorage={this.getSessionStorage}
                                       deleteSessionStorage={this.deleteSessionStorage}
                                       authenticate={this.authenticate}
                            />
                            <Message message={this.state.message}
                                     messageClass={this.state.messageClass}
                            />
                            {dataTable}
                            <Footer footer={App.APP_DETAILS.footerText}
                                    copyright={App.APP_DETAILS.copyright}
                                    version={App.APP_DETAILS.version}
                            />
                            <StockUpdateModal
                                stockUpdateData={this.state.stockUpdateData}
                                stockUpdateMeta={this.state.stockUpdateMeta}
                                openStockUpdateModal={this.state.stockUpdateModalOpen}
                                API_OPTIONS={App.API_OPTIONS}
                                setStockUpdateModalState={this.setStockUpdateModalState}
                                setStockUpdateRecordState={this.setStockUpdateRecordState}
                                setMessage={this.setMessage}
                            />
                            <ApiRequest
                                API_OPTIONS={App.API_OPTIONS}
                                stockUpdateMeta={this.state.stockUpdateMeta}
                                stockRecordMeta={this.state.stockRecordMeta}
                                stockUpdateData={this.state.stockUpdateData}
                                authMeta={this.state.authMeta}
                                apiTrigger={this.state.apiTrigger}
                                csrfToken={this.state.csrfToken}
                                setStockRecordState={this.setStockRecordState}
                                setStockUpdateRecordState={this.setStockUpdateRecordState}
                                getSessionStorage={this.getSessionStorage}
                                setSessionStorage={this.setSessionStorage}
                                disarmAPI={this.disarmAPI}
                                setMessage={this.setMessage}
                                authenticate={this.authenticate}
                            />
                        </div>
                    </div>
                </div>
            </div>
        );
    };
}

ReactDOM.render(
    <App/>, document.getElementById('react-app'));