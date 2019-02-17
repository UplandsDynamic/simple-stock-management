/* react */
import React from 'react';
/* app components */
import LoginForm from './loginform.js';
import DataTable from './data-table.js';
import StockUpdateModal from './stock-update-modal.js';
import ApiRequest from './api-request.js';
import Message from './message.js';
import Footer from './footer.js';
/* cookies */
import Cookies from 'js-cookie';
/* helpers */
import cloneDeep from "lodash.clonedeep"
/* axios */
import axios from 'axios/index';
/* css */
import './css/index.css';
/* font awesome icons */
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare);


axios.defaults.withCredentials = true;

/* App root */
class App extends React.Component {

    constructor(props) {
        super(props); // makes 'this' refer to component (i.e. like python self)
        /* set local state. Only initialise stockData with required defaults for 1st request and
        BEFORE data returned. Rest all added in call to stockDataHandler called after response received
        */
        this.apiOptions = {
            /* used to define available API options in the api-request component */
            GET_STOCK: {method: 'GET', desc: 'request to get stock data'},
            PATCH_STOCK: {method: 'PATCH', desc: 'PATCH request to update stock data'},
            ADD_STOCK: {method: 'POST', desc: 'POST request to add stock data'},
            DELETE_STOCK_LINE: {method: 'DELETE', desc: 'DELETE request to delete stock line'},
            POST_AUTH: {method: 'POST', desc: 'POST request to for authorization'},
            PATCH_CHANGE_PW: {method: 'PATCH', desc: 'PATCH request to for changing password'},
        };
        this.initialState = {
            stockRecordData: {data: {results: []}},
            stockRecordMeta: {
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
            },
            stockUpdateData: {
                units_total: 0,
                unit_price: 0.00,
                desc: '',
                sku: ''
            },
            stockUpdateMeta: {
                cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
                url: null,
                userIsAdmin: false,
                newRecord: false,
                deleteRecord: false,
            },
            authMeta: {
                url: `${process.env.REACT_APP_API_ROUTE}/api-token-auth/`,
                change_pw_url: `${process.env.REACT_APP_API_ROUTE}/v1/change-password/`,
                authenticated: Boolean(sessionStorage.getItem('apiToken')),
                cacheControl: 'no-cache',
                requestData: null,
            },
            stockUpdateModalOpen: false,
            apiMode: null,  // will be one of apiOptions when triggered
            message: null,
            messageClass: '',
            greeting: process.env.REACT_APP_GREETING,
            csrfToken: null
        };
        this.state = cloneDeep(this.initialState);
    }

    componentDidMount() {
        this.setState({csrfToken: this.getCSRFToken()})
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


    authenticate = ({apiMode = null, requestData = null, auth = false} = {}) => {
        // ensure token deleted if auth false
        if (!auth) {
            this.deleteSessionStorage(['apiToken', 'username'])
        }
        // triggers API to get auth token
        this.setState({
            apiMode: apiMode,
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
            stockUpdateData: {...this.initialState.stockUpdateData},
            stockUpdateMeta: {...this.initialState.stockUpdateMeta},
        })
    };

    setStockRecordState = ({stockRecord, updatedData, apiMode = null} = {}) => {
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
        if (metaState.page < 1) {
            metaState.page = 1
        }
        // set new state, then once done (as callback) reset state data to defaults
        this.setState({
            stockRecordData: recordState, stockRecordMeta: metaState,
            apiMode: apiMode,
        }, this.resetUpdateDataState);
        return true
    };

    setStockUpdateRecordState = ({record = null, apiMode = null, clearData = false} = {}) => {
        /*
        method to update the state for the record being edited (PATCH request), or add
        new record
         */
        // clear updateData if requested
        if (clearData) {
            this.setState({stockUpdateData: this.initialState.stockUpdateData});
        }
        let recordState = this.state.stockUpdateData;
        let metaState = this.state.stockUpdateMeta;
        let admin = false;
        Object.entries(record && record.data ? record.data : recordState).forEach((kvArray) => {
            /*add data to record (removing unnecessary elements & assigning user admin status
            to stockUpdateMeta instead */
            if (kvArray[0] === 'user_is_admin') {
                admin = kvArray[1]
            }
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
            apiMode: apiMode
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
        if (actionCancelled) {
            this.resetUpdateDataState()
        }
    };

    clearApiMode = () => {
        // disables API active state
        this.setState({apiMode: null})
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
                           apiOptions={this.apiOptions}
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
                                       apiOptions={this.apiOptions}
                                       authMeta={this.state.authMeta}
                                       greeting={process.env.REACT_APP_GREETING}
                                       getSessionStorage={this.getSessionStorage}
                                       deleteSessionStorage={this.deleteSessionStorage}
                                       authenticate={this.authenticate}
                            />
                            <Message message={this.state.message}
                                     messageClass={this.state.messageClass}
                            />
                            {dataTable}
                            <Footer footer={process.env.REACT_APP_FOOTER}
                                    copyright={process.env.REACT_APP_COPYRIGHT}
                                    version={process.env.REACT_APP_VERSION}
                            />
                            <StockUpdateModal
                                stockUpdateData={this.state.stockUpdateData}
                                stockUpdateMeta={this.state.stockUpdateMeta}
                                openStockUpdateModal={this.state.stockUpdateModalOpen}
                                apiOptions={this.apiOptions}
                                setStockUpdateModalState={this.setStockUpdateModalState}
                                setStockUpdateRecordState={this.setStockUpdateRecordState}
                                setMessage={this.setMessage}
                            />
                            <ApiRequest
                                apiOptions={this.apiOptions}
                                stockUpdateMeta={this.state.stockUpdateMeta}
                                stockRecordMeta={this.state.stockRecordMeta}
                                stockUpdateData={this.state.stockUpdateData}
                                authMeta={this.state.authMeta}
                                apiMode={this.state.apiMode}
                                csrfToken={this.state.csrfToken}
                                setStockRecordState={this.setStockRecordState}
                                setStockUpdateRecordState={this.setStockUpdateRecordState}
                                getSessionStorage={this.getSessionStorage}
                                setSessionStorage={this.setSessionStorage}
                                clearApiMode={this.clearApiMode}
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

export default App;
