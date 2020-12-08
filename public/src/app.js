/*version*/
import APP_VERSION from './version';
/* react */
import React from 'react';
/* app components */
import Header from './header.js';
import DataTable from './data-table.js';
import StockUpdateModal from './stock-update-modal.js';
import TruckModal from './truck.js';
import Message from './message.js';
import Footer from './footer.js';
/* functions */
import processRequest from "./api";
/* cookies */
import Cookies from 'js-cookie';
/* axios */
import axios from 'axios/index';
/* css */
import './css/index.css';
/* font awesome icons */
import { library } from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit, faTruck, faUserCircle, faEye
} from '@fortawesome/free-solid-svg-icons';

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare, faTruck, faUserCircle, faEye);


axios.defaults.withCredentials = true;

/* App root */
class App extends React.Component {

    constructor(props) {
        super(props); // makes 'this' refer to component (i.e. like python self)
        /* set local state. Only initialise stockData with required defaults for 1st request and
        BEFORE data returned. Rest all added in call to stockDataHandler called after response received
        */
        this.ACCOUNT_MODES = {
            WAREHOUSE: 'Main stock warehouse',
            STORE: 'Stores'
        }
        this.apiOptions = {
            /* used to define available API options in the api-request component */
            GET_STOCK: { requestType: 'get_stock', method: 'GET', desc: 'request to get stock data' },
            GET_ACCOUNT_STOCK: { requestType: 'get_account_stock', method: 'GET', desc: 'request to get account stock data' },
            GET_TAKE_STOCK: { requestType: 'get_take_stock', method: 'GET', desc: 'request to initiate stock take (count)' },
            PATCH_STOCK: { requestType: 'patch_stock', method: 'PATCH', desc: 'PATCH request to update stock data' },
            PATCH_ACCOUNT_STOCK: { requestType: 'patch_account_stock', method: 'PATCH', desc: 'PATCH request to update account stock data' },
            ADD_STOCK: { requestType: 'add_stock', method: 'POST', desc: 'POST request to add stock data' },
            ADD_ACCOUNT_STOCK: { requestType: 'add_account_stock', method: 'POST', desc: 'POST request to add account stock line' },
            DELETE_STOCK_LINE: { requestType: 'delete_stock_line', method: 'DELETE', desc: 'DELETE request to delete stock line' },
            DELETE_ACCOUNT_STOCK_LINE: { requestType: 'delete_account_stock_line', method: 'DELETE', desc: 'DELETE request to delete account stock line' },
            POST_AUTH: { requestType: 'post_auth', method: 'POST', desc: 'POST request to for authorization' },
            POST_LOGOUT: { requestType: 'post_logout', method: 'POST', desc: 'POST request to for logout of server' },
            PATCH_CHANGE_PW: { requestType: 'patch_change_pw', method: 'PATCH', desc: 'PATCH request to for changing password' },
        };

        this.initialState = {
            stockRecord: {
                meta: {
                    page: 1,
                    limit: process.env.REACT_APP_ROWS_PER_TABLE,
                    pagerMainSize: process.env.REACT_APP_PAGER_MAIN_SIZE,
                    pagerEndSize: process.env.REACT_APP_PAGER_END_SIZE,
                    pageOrderBy: '',
                    pageOrderDir: '',
                    previous: null,
                    next: null,
                    cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
                    search: ''
                },
                data: {
                    results: [],
                    updateData: {}
                }
            },
            authMeta: {
                authenticated: false,
                userIsAdmin: false,
            },
            updateModalOpen: {
                state: false,
                accountRecord: {},
                deleteRecord: false,
                newRecord: false
            },
            truckModalOpen: false,
            truck: [],
            message: null,
            messageClass: '',
            greeting: process.env.REACT_APP_GREETING,
            csrfToken: null,
            accountMode: this.ACCOUNT_MODES.WAREHOUSE // set default as WAREHOUSE
        }
        this.state = JSON.parse(JSON.stringify(this.initialState));
        // bind methods to be passed as props
        this.changeTruckUnits = this.changeTruckUnits.bind(this);
        this.emptyTruck = this.emptyTruck.bind(this);
        this.getTruck = this.getTruck.bind(this);
        this.loadTruck = this.loadTruck.bind(this);
        this.setAccountMode = this.setAccountMode.bind(this);
        this.getRecordsHandler = this.getRecordsHandler.bind(this);
        this.stockTakeHandler = this.stockTakeHandler.bind(this);
        this.getStyles = this.getStyles.bind(this);
    }

    getStyles() {
        // contextual overrides (inline) for CSS stylesheet
        if (this.state.accountMode === this.ACCOUNT_MODES.STORE) {
            return {
                messageBackground: { backgroundColor: 'teal', color: 'yellow' },
                mainBackground: { backgroundColor: '#000023', color: 'yellow' },
                recordTable: { backgroundColor: '#000033', color: 'yellow' },
                pagerButtons: { backgroundColor: '#000033', color: 'yellow' },
                currentPage: { backgroundColor: 'yellow', color: '#000033' }
            }
        } else return {
            messageBackground: { backgroundColor: 'teal', color: 'yellow' },
            mainBackground: {backgroundColor: '#002300'}
        };
    }

    componentDidMount() {
        this.setState({ csrfToken: this.getCSRFToken() });
        // kick off: attempt to authenticate (new authentication also requests stock data)
        this.setAuthentication();
    }

    componentDidUpdate() {
    }

    getCSRFToken = () => {
        return Cookies.get('csrftoken')
    };

    setSessionStorage = ({ key, value }) => {
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

    setAuthentication = () => {
        let authenticated = !!this.getSessionStorage('token');
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        Object.assign(clonedAuthMeta, { authenticated });
        // set authentication state and fetch new stock records when done (in a callback)
        this.setState({ authMeta: { ...clonedAuthMeta } }, this.getRecordsHandler);
    };


    setAuthorized = ({ role = 'admin', state = false } = {}) => {
        // called after each api response returning stock data
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        if (role === 'admin') {
            Object.assign(clonedAuthMeta, { userIsAdmin: state });
        }
        this.setState({ authMeta: { ...clonedAuthMeta } });
    };

    setAccountMode = () => {
        // reset page so switching modes always opens page 1 of results
        this.setState({ // toggle account mode & get appropriate records
            accountMode: this.state.accountMode === this.ACCOUNT_MODES.WAREHOUSE ?
                this.ACCOUNT_MODES.STORE : this.ACCOUNT_MODES.WAREHOUSE,
            stockRecord: {
                data: this.state.stockRecord.data,
                meta: { ...this.state.stockRecord.meta, page: 1 }
            }
        }, () => this.getRecordsHandler({ notifyResponse: true }));
        // get records for the account mode
    };

    setStockRecordState = ({ newStockRecord } = {}) => {
        /*
        method to update state for record being retrieved (GET request)
         */
        let { page } = newStockRecord.meta;
        if (newStockRecord) {
            // ensure page never < 1
            let updatedPage = page < 1 ? 1 : page;
            Object.assign(newStockRecord.meta, { page: updatedPage });
            // set user admin status to what was returned from api in stock record data
            if (!!newStockRecord.data.results.length && Object.prototype.hasOwnProperty.call(newStockRecord.data.results[0], 'user_is_admin')
            ) {
                this.setAuthorized({ role: 'admin', state: !!newStockRecord.data.results[0].user_is_admin })
            }
        }
        this.setState({ stockRecord: newStockRecord });
    };

    openTruckModalHandler = ({ returnedRecords = null, state = false, actionCancelled = false } = {}) => {
        /*
        method to open the truck modal
         */
        if (!state) {  // actions to do when modal set to closed
            this.setState({ truckModalOpen: state });   // close it first, to avoid showing reset data values
            if (!actionCancelled) {  // actions to do if CANCEL was NOT clicked when it closes (i.e. action time)
                let stockRecordCopy = JSON.parse(JSON.stringify(this.state.stockRecord));
                returnedRecords.forEach((returnedRecord) => {
                    stockRecordCopy.data.results.forEach((stockRecord, i) => {
                        if (stockRecord.id === returnedRecord.data.id) {
                            stockRecordCopy.data.results[i].units_total = returnedRecord.data.units_total;
                        }
                    })
                });
                this.setState({ stockRecord: stockRecordCopy });
                this.setMessage({
                    message: 'Transfer successfully initiated! Check email for confirmation of transferred units.',
                    messageClass: 'alert alert-success'
                });
            }
        } else { // actions to do when modal set to open
            this.getTruck();  // set state with up-to-date truck data
            this.setState({ truckModalOpen: state });
        }
    };

    getTruck() {
        const truck = JSON.parse(localStorage.getItem('truck'));
        if (truck && truck.user === this.getSessionStorage('username')) {
            this.setState({ truck: truck.data });
            return truck.data;
        }
        this.setState({ truck: [] });
        return [];
    }

    emptyTruck() {
        localStorage.removeItem('truck');
    }

    loadTruck({ cargo = null } = {}) {
        let exists = false;
        let truck = this.getTruck();
        if (truck.length > 0) {
            for (let consignment = 0; consignment < truck.length; consignment++) {
                if (truck[consignment].cargo.id === cargo.id) {
                    truck[consignment].cargo = { ...cargo };
                    exists = true;
                }
            }
        }
        if (!exists) truck.push({ cargo });
        const truckData = JSON.stringify({ user: this.getSessionStorage('username'), data: truck })
        localStorage.setItem('truck', truckData);
    }

    changeTruckUnits({ consignmentListIndex = null, func = null, cargo = null } = {}) {
        if (consignmentListIndex !== null) {
            let truckLoad = this.state.truck;
            if (func === 'add') {
                let units = truckLoad[consignmentListIndex].cargo.units_to_transfer;
                if (cargo.start_units_total >= units + 1) {
                    truckLoad[consignmentListIndex].cargo.units_to_transfer++;
                }
            }
            if (func === 'minus') {
                if (cargo.units_total >= 0 && cargo.units_to_transfer > 1) {
                    truckLoad[consignmentListIndex].cargo.units_to_transfer--;
                }
            }
            if (func === 'clear') {
                truckLoad.splice(consignmentListIndex, 1);
            }
            const truckData = JSON.stringify({ user: this.getSessionStorage('username'), data: truckLoad })
            localStorage.setItem('truck', truckData);
            this.setState({ truck: truckLoad });
        }
    }

    getRecordsHandler = ({ stockRecord = this.state.stockRecord, url = null, notifyResponse = true } = {}) => {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({
                url: url,
                stockRecord: stockRecord,
                apiMode: this.state.accountMode === this.ACCOUNT_MODES.WAREHOUSE ?
                    this.apiOptions.GET_STOCK : this.apiOptions.GET_ACCOUNT_STOCK
            });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        if (notifyResponse) {
                            this.setMessage({
                                message: 'Records successfully retrieved!',
                                messageClass: 'alert alert-success'
                            });
                        }
                        Object.assign(stockRecord.data, { ...response.data });
                        Object.assign(stockRecord.meta, { ...stockRecord.meta });
                        // update stockRecordMeta state in app.js
                        this.setStockRecordState({ newStockRecord: stockRecord });
                    }
                }).catch(error => {
                    let message = '';
                    console.log(error);
                    if (error.response.status === 401) {
                        message = 'User is unauthorised. Perhaps a stock take is in progress.';
                    } else {
                        message = `An API error has occurred: ${error.response.data.detail}`;
                    }
                    this.setMessage({ message, messageClass: 'alert alert-danger' });
                    this.setStockRecordState({ newStockRecord: stockRecord });
                });
            }
        }
        return false;
    };

    stockTakeHandler = () => {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({ apiMode: this.apiOptions.GET_TAKE_STOCK });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        this.setMessage({
                            message: 'Stock take successfully initiated!',
                            messageClass: 'alert alert-success'
                        });
                    }
                }).catch(error => {
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred. Stock take failed!',
                        messageClass: 'alert alert-danger'
                    });
                });
            }
        }
        return false;
    }

    openStockUpdateModalHandler = ({ stockRecord = this.state.stockRecord, deleteRecord = false,
        newRecord = false } = {}) => {
        /*
        method to open the stock addition/update/delete modal
         */
        Object.assign(stockRecord, { ...stockRecord });
        this.setStockRecordState({ newStockRecord: stockRecord });
        this.setStockUpdateModalState({ state: true, deleteRecord, newRecord });
    };

    setStockUpdateModalState = ({
        stockRecord = this.state.stockRecord, state = false, actionCancelled = false,
        deleteRecord = false, newRecord = false } = {}) => {
        /*
        method to update the state for the modal open/close state. If closed, ensure ensure meta flags cleared (
        e.g. deleteRecord), and reset the update data.
         */
        if (!state) {  // actions to do when modal set to closed
            this.setState({ updateModalOpen: { state, deleteRecord, newRecord } });   // close it first, to avoid showing reset data values
            stockRecord.data.updateData = {};  // clear transient update data
            this.setStockRecordState({ newStockRecord: stockRecord });
            if (!actionCancelled) {  // if was not cancelled, request updated data from API following the actions.
                this.getRecordsHandler({ stockRecord, notifyResponse: false });
            }
        } else { // actions to do when modal set to open
            // always update the updateData with truck data (held in local storage) if any
            let stockRecordClone = JSON.parse(JSON.stringify(stockRecord));
            let truck = this.getTruck();
            if (truck.length > 0) {
                let recordID = stockRecordClone.data.updateData.id;
                truck.forEach((consignment) => {
                    if (recordID === consignment.cargo.id) {
                        Object.assign(stockRecordClone.data.updateData, consignment.cargo)
                    }
                });
                this.setState({ stockRecord: stockRecordClone });
                stockRecordClone = null;
            }
            this.setState({
                updateModalOpen: { state, deleteRecord, newRecord }
            });
        }
    };

    setMessage = ({ message = null, messageClass = '' } = {}) => {
        this.setState({ message: message, messageClass: messageClass });
    };

    render() {
        let dataTable;
        dataTable = (
            <DataTable stockRecord={this.state.stockRecord}
                apiOptions={this.apiOptions}
                setStockRecordState={this.setStockRecordState}
                openStockUpdateModalHandler={this.openStockUpdateModalHandler}
                stockTakeHandler={this.stockTakeHandler}
                setMessage={this.setMessage}
                getRecordsHandler={this.getRecordsHandler}
                authMeta={this.state.authMeta}
                accountMode={this.state.accountMode}
                accountModes={this.ACCOUNT_MODES}
                getStyles={this.getStyles}
            />);
        return (
            <React.Fragment>
                <div className={'app-main'} style={this.getStyles().mainBackground}>
                    <div className={'container'}>
                        <div className={'row'}>
                            <div className={'col-12'}>
                                <Header authMeta={this.state.authMeta}
                                    apiOptions={this.apiOptions}
                                    csrfToken={this.state.csrfToken}
                                    setMessage={this.setMessage}
                                    getSessionStorage={this.getSessionStorage}
                                    setSessionStorage={this.setSessionStorage}
                                    deleteSessionStorage={this.deleteSessionStorage}
                                    setAuthentication={this.setAuthentication}
                                    openTruck={this.openTruckModalHandler}
                                    accountMode={this.state.accountMode}
                                    accountModes={this.ACCOUNT_MODES}
                                    setAccountMode={this.setAccountMode}
                                />
                                <Message message={this.state.message}
                                    messageClass={this.state.messageClass}
                                    accountModes={this.ACCOUNT_MODES}
                                    accountMode={this.state.accountMode}
                                    getStyles={this.getStyles}
                                />
                                {dataTable}
                                <StockUpdateModal
                                    stockRecord={this.state.stockRecord}
                                    authMeta={this.state.authMeta}
                                    openStockUpdateModal={this.state.updateModalOpen}
                                    apiOptions={this.apiOptions}
                                    loadTruck={this.loadTruck}
                                    setStockUpdateModalState={this.setStockUpdateModalState}
                                    setStockRecordState={this.setStockRecordState}
                                    setMessage={this.setMessage}
                                    accountModes={this.ACCOUNT_MODES}
                                    accountMode={this.state.accountMode}
                                />
                                <TruckModal
                                    stockRecord={this.state.stockRecord}
                                    authMeta={this.state.authMeta}
                                    openTruckModal={this.state.truckModalOpen}
                                    apiOptions={this.apiOptions}
                                    changeTruckUnits={this.changeTruckUnits}
                                    emptyTruck={this.emptyTruck}
                                    openTruckModalHandler={this.openTruckModalHandler}
                                    setMessage={this.setMessage}
                                    truck={this.state.truck}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <Footer footer={process.env.REACT_APP_FOOTER}
                    copyright={process.env.REACT_APP_COPYRIGHT}
                    version={APP_VERSION}
                />
            </React.Fragment>
            
        );
    }
}

export default App;

/* GENERAL NOTES
- state.stockRecord should only ever be set using setStockRecordState.
 */