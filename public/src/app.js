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
    faTrashAlt, faEdit, faTruck
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare, faTruck);


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
            GET_STOCK: { requestType: 'get_stock', method: 'GET', desc: 'request to get stock data' },
            PATCH_STOCK: { requestType: 'patch_stock', method: 'PATCH', desc: 'PATCH request to update stock data' },
            ADD_STOCK: { requestType: 'add_stock', method: 'POST', desc: 'POST request to add stock data' },
            DELETE_STOCK_LINE: {
                requestType: 'delete_stock_line',
                method: 'DELETE',
                desc: 'DELETE request to delete stock line'
            },
            POST_AUTH: { requestType: 'post_auth', method: 'POST', desc: 'POST request to for authorization' },
            PATCH_CHANGE_PW: {
                requestType: 'patch_change_pw',
                method: 'PATCH',
                desc: 'PATCH request to for changing password'
            },
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
                    updateData: {
                        id: '',
                        sku: '',
                        desc: '',
                        units_total: 0,
                        unit_price: 0,
                        units_to_transfer: 0,
                        start_units_total: 0
                    }
                }
            },
            authMeta: {
                authenticated: false,
                userIsAdmin: false,
            },
            stockUpdateModalOpen: { state: false, deleteRecord: false, newRecord: false },
            truckModalOpen: false,
            message: null,
            messageClass: '',
            greeting: process.env.REACT_APP_GREETING,
            csrfToken: null,
        };
        this.state = JSON.parse(JSON.stringify(this.initialState));
        // bind methods to be passed as props
        this.changeTruckUnits = this.changeTruckUnits.bind(this);
        this.emptyTruck = this.emptyTruck.bind(this);
        this.getTruck = this.getTruck.bind(this);
        this.loadTruck = this.loadTruck.bind(this);
    }

    componentDidMount() {
        this.setState({ csrfToken: this.getCSRFToken() });
        // kick off: attempt to authenticate (new authentication also requests stock data)
        this.setAuthentication();
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
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
            if (!!newStockRecord.data.results.length && newStockRecord.data.results[0].hasOwnProperty('user_is_admin')
            ) {
                this.setAuthorized({ role: 'admin', state: !!newStockRecord.data.results[0].user_is_admin })
            }
        }
        this.setState({ stockRecord: newStockRecord });
    };

    openStockUpdateModalHandler = ({ stockRecord = null, deleteRecord = false, newRecord = false } = {}) => {
        /*
        method to open the stock addition/update/delete modal
         */
        Object.assign(stockRecord, { ...stockRecord });
        this.setStockRecordState({ newStockRecord: stockRecord });
        this.setStockUpdateModalState({ state: true, deleteRecord, newRecord });
    };

    openTruckModalHandler = ({ returnedRecords = null, state = false, actionCancelled = false } = {}) => {
        /*
        method to open the truck modal
         */
        if (!state) {  // actions to do when modal set to closed
            this.setState({ truckModalOpen: state });   // close it first, to avoid showing reset data values
            if (!actionCancelled) {  // actions to do if CANCEL was NOT clicked when it closes (i.e. action time)
                let stockRecordCopy = JSON.parse(JSON.stringify(this.state.stockRecord));
                returnedRecords.forEach((returnedRecord, index) => {
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
            this.setState({ truck: this.getTruck() }); // refresh truck data from local storage
            this.setState({ truckModalOpen: state });
        }
    };

    getTruck() {
        const truck = localStorage.getItem('truck');
        return truck ? JSON.parse(localStorage.getItem('truck')) : [];
    };

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
        localStorage.setItem('truck', JSON.stringify(truck));
    }

    changeTruckUnits({ consignmentListIndex = null, func = null, cargo = null } = {}) {
        if (consignmentListIndex !== null) {
            let truckLoad = this.getTruck();
            if (func === 'add') {
                let units = truckLoad[consignmentListIndex].cargo.units_to_transfer;
                if (cargo.start_units_total >= units + 1) {
                    truckLoad[consignmentListIndex].cargo.units_to_transfer++;
                }
            }
            if (func === 'minus') {
                if (cargo.units_total > 0 && cargo.units_to_transfer > 1) {
                    truckLoad[consignmentListIndex].cargo.units_to_transfer--;
                }
            }
            if (func === 'clear') {
                truckLoad.splice(consignmentListIndex, 1);
            }
            localStorage.setItem('truck', JSON.stringify(truckLoad));
            this.setState({ truck: this.getTruck() })
        }
    }

    getRecordsHandler = ({ stockRecord = this.state.stockRecord, url = null, notifyResponse = true } = {}) => {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({
                url: url,
                stockRecord: stockRecord,
                apiMode: this.apiOptions.GET_STOCK
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
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred',
                        messageClass: 'alert alert-danger'
                    });
                    this.setStockRecordState({
                        newStockRecord: stockRecord,
                    });
                });
            }
        }
        return false
    };

    setStockUpdateModalState = ({
        stockRecord = this.state.stockRecord, state = false, actionCancelled = false,
        deleteRecord = false, newRecord = false
    } = {}) => {
        /*
        method to update the state for the modal open/close state. If closed, ensure ensure meta flags cleared (
        e.g. deleteRecord), and reset the update data.
         */
        if (!state) {  // actions to do when modal set to closed
            this.setState({ stockUpdateModalOpen: { state, deleteRecord, newRecord } });   // close it first, to avoid showing reset data values
            Object.assign(stockRecord.data.updateData, { ...this.initialState.stockRecord.data.updateData });
            this.setStockRecordState({ newStockRecord: stockRecord });
            if (!actionCancelled) {  // if was not cancelled, request updated data from API following the actions.
                this.getRecordsHandler({ stockRecord, notifyResponse: false });
            }
        } else { // actions to do when modal set to open
            // always update the updateData with truck data (held in local storage) if any
            let stockRecordClone = JSON.parse(JSON.stringify(stockRecord));
            let truck = this.getTruck();
            let recordID = stockRecordClone.data.updateData.id;
            truck.forEach((consignment) => {
                if (recordID === consignment.cargo.id) {
                    Object.assign(stockRecordClone.data.updateData, consignment.cargo)
                }
            });
            this.setState({ stockRecord: stockRecordClone });
            stockRecordClone = null;
            this.setState({ stockUpdateModalOpen: { state, deleteRecord, newRecord } });
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
                setMessage={this.setMessage}
                getRecordsHandler={this.getRecordsHandler}
                authMeta={this.state.authMeta}
            />
        );
        return (
            <div className={'app-main'}>
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
                            />
                            <Message message={this.state.message}
                                messageClass={this.state.messageClass}
                            />
                            {dataTable}
                            <Footer footer={process.env.REACT_APP_FOOTER}
                                copyright={process.env.REACT_APP_COPYRIGHT}
                                version={APP_VERSION}
                            />
                            <StockUpdateModal
                                stockRecord={this.state.stockRecord}
                                authMeta={this.state.authMeta}
                                openStockUpdateModal={this.state.stockUpdateModalOpen}
                                apiOptions={this.apiOptions}
                                loadTruck={this.loadTruck}
                                setStockUpdateModalState={this.setStockUpdateModalState}
                                setStockRecordState={this.setStockRecordState}
                                setMessage={this.setMessage}
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
                                getTruck={this.getTruck}
                            />
                        </div>
                    </div>
                </div>
            </div>
        );
    };
}

export default App;

/* GENERAL NOTES
- state.stockRecord should only ever be set using setStockRecordState.
 */