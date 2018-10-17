import React from 'react';
import axios from 'axios/index';
import Env from './env.jsx';

class ApiRequest extends React.Component {

    constructor(props) {
        super(props);
        // Remember! This binding is necessary to make `this` work in the callback
        // keep real-time props changes in component state
        this.setFormApi = this.setFormApi.bind(this);
        this.state = {
            activeRequest: false,
            currentOrderBy: '',
            currentOrderDir: '',
            currentPage: 1,
        };
    }

    componentWillMount() {
    }

    componentWillUnmount() {
    }

    componentWillReceiveProps(nextProps) {
        let orderDir, url;
        let getStockMeta = nextProps.stockRecordMeta;
        let getStockData = nextProps.stockRecordData;
        let updateStockMeta = nextProps.stockUpdateMeta;
        let updateStockData = nextProps.stockUpdateData;
        let authMeta = nextProps.authMeta;
        let csrfToken = nextProps.csrfToken;
        switch (nextProps.apiTrigger) {
            case this.props.API_OPTIONS.GET_STOCK:  // get stock data
                orderDir = this.generateRecordRequestOrder(getStockMeta);
                url = getStockMeta.url ? getStockMeta.url :
                    `${Env().apiDataRoot}/stock/?limit=${getStockMeta.limit}` +
                    `&offset=${(getStockMeta.page * getStockMeta.limit) - getStockMeta.limit}` +
                    `&order_by=${orderDir}${getStockMeta.orderBy}&desc=${getStockMeta.search}`;
                this.props.setStockRecordState({
                    stockRecord: {meta: {orderDir: orderDir, url: null}}
                });// set new order dir state
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestType: this.props.API_OPTIONS.GET_STOCK,
                    requestMeta: getStockMeta
                });
                break;
            case this.props.API_OPTIONS.PATCH_STOCK:  // update stock data
                url = updateStockData ?
                    `${Env().apiDataRoot}/stock/${updateStockData.id}/` :
                    updateStockMeta.url;
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestData: updateStockData,
                    requestType: this.props.API_OPTIONS.PATCH_STOCK,
                    requestMeta: updateStockMeta
                });
                break;
            case this.props.API_OPTIONS.ADD_STOCK:  // update stock data
                url = updateStockMeta.url;
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestData: updateStockData,
                    requestType: this.props.API_OPTIONS.ADD_STOCK,
                    requestMeta: updateStockMeta
                });
                break;
            case this.props.API_OPTIONS.DELETE_STOCK_LINE: // delete stock line
                url = updateStockData ? `${Env().apiDataRoot}/stock/${updateStockData.id}/` :
                    null;
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestData: updateStockData,
                    requestType: this.props.API_OPTIONS.DELETE_STOCK_LINE,
                    requestMeta: updateStockMeta
                });
                break;
            case this.props.API_OPTIONS.POST_AUTH:  // get auth token
                url = authMeta.url;
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestType: this.props.API_OPTIONS.POST_AUTH,
                    requestData: {
                        username: authMeta.requestData.data.username,
                        password: authMeta.requestData.data.password
                    }
                });
                break;
            case this.props.API_OPTIONS.PATCH_CHANGE_PW:  // change password
                url = `${authMeta.change_pw_url}${authMeta.requestData.data.username}/`;
                this.sendRequest({
                    url: url,
                    csrfToken: csrfToken,
                    requestType: this.props.API_OPTIONS.PATCH_CHANGE_PW,
                    requestData: {
                        old_password: authMeta.requestData.data.old_password,
                        new_password: authMeta.requestData.data.new_password
                    }
                });
                break;
            default:
            // console.log('Not calling API, nothing to do ...')
        }
    }

    setFormApi(formApi) {
        this.formApi = formApi;
    }

    generateRecordRequestOrder(requestMeta) {
        /*
        Method to generate the request ordering.
        Reverses ordering if column clicked when
        already ordered on the same column.
        Otherwise, defaults to ascending order.

        Note: page always reverts to page 1 IF column clicked to change order on any
        page other than 1, as new ordering is requested from API. Needs to return to page 1 to
        display the newly requested (differently sorted) pages -
        otherwise the current page would display any data that happened to correspond to that
        page of newly received data, and that wouldn't be expected behaviour.
        Could also add method (& UI link/button/widget) for columns to LOCALLY order/sort presently
        displayed page data (without an API request) if required.
         */
        if (requestMeta.preserveOrder) return requestMeta.orderDir; // end here if current order to be preserved
        if (this.state.currentOrderBy !== requestMeta.orderBy) {
            this.setState({
                currentOrderDir: '',
                currentOrderBy: requestMeta.orderBy,
            });
            return ''
        }
        if (this.state.currentPage === requestMeta.page) {
            let newOrderDir = this.state.currentOrderDir === '-' ? '' : "-";
            this.setState({
                currentOrderDir: newOrderDir
            });
            return newOrderDir;
        } else {
            this.setState({
                currentPage: requestMeta.page
            });
            return this.state.currentOrderDir
        }
    }

    sendRequest({url = null, requestData = null, requestMeta = null, requestType = null, csrfToken = null} = {}) {
        this.props.disarmAPI(); // disarm the API now the command has been actioned
        if (!this.state.activeRequest && url && requestType) {
            this.setState({
                activeRequest: true,
            });
            // make request
            //console.log('Sending request to API');
            axios({
                method: requestType.method,
                url: url,
                responseType: 'json',
                data: requestData ? requestData : {},
                //auth: {},
                headers: {
                    Authorization: this.props.getSessionStorage('apiToken') ?
                        `Token ${this.props.getSessionStorage('apiToken')}` : null,
                    'cache-control': requestMeta ? requestMeta.cacheControl : 'no-cache',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                } // additional headers here
            }).then((response) => {
                this.setState({activeRequest: false});
                this.handleAPIResponse({
                    requestData: requestData, requestType: requestType,
                    response: response
                });
            }).catch(error => {
                this.setState({activeRequest: false});
                this.handleAPIResponse({error: error, requestType: requestType});
            });
        } else {
            //console.log('Request already active or no URL set!')
        }
    }

    handleAPIResponse({requestData = null, requestType = null, response = null, error = null} = {}) {
        if (error) {
            switch (requestType) {
                case this.props.API_OPTIONS.GET_STOCK:
                    this.props.setMessage({
                        message: error.response ? error.response.data[0] : error,
                        messageClass: 'alert alert-danger'
                    });
                    break;
                case this.props.API_OPTIONS.PATCH_STOCK:
                case this.props.API_OPTIONS.ADD_STOCK:
                case this.props.API_OPTIONS.DELETE_STOCK_LINE:
                    let msgArray = [];
                    this.props.setStockUpdateRecordState({clearData: true}); // clear data for next time
                    if (error.response && error.response.data) {
                        Object.keys(error.response.data).forEach((key) => msgArray.push(error.response.data[key]));
                        this.props.setMessage({
                            message: msgArray.length >= 0 ? msgArray.join(', ') : error,
                            messageClass: 'alert alert-danger'
                        });
                    } else {
                        this.props.setMessage({
                            message: 'An api error occurred!',
                            messageClass: 'alert alert-danger'
                        });
                    }
                    break;
                case this.props.API_OPTIONS.POST_AUTH:
                case this.props.API_OPTIONS.PATCH_CHANGE_PW:
                    let message = 'An error occurred! ';
                    if (error.response) {
                        if (error.response.data) {
                            if (error.response.data.old_password) {
                                message += `Old password error: ${error.response.data.old_password} `;
                            }
                            if (error.response.data.new_password) {
                                message += `New password error: ${error.response.data.new_password} `;
                            }
                        } else if (error.response.detail) {
                            message += `Error detail: ${error.response.detail} `;
                        }
                    }
                    else {
                        message += error
                    }
                    this.props.setMessage({
                        message: message,
                        messageClass: 'alert alert-danger'
                    });
                    this.props.authenticate({auth: false}); // ensure unauthenticated status is set
                    break;
                default:
                    this.props.setMessage({
                        message: 'An api error occurred!',
                        messageClass: 'alert alert-danger'
                    });
            }
        } else {
            switch (requestType) {
                case this.props.API_OPTIONS.GET_STOCK:
                    this.props.setStockRecordState({
                        stockRecord: {data: response, meta: {preserveOrder: false}}
                    });
                    break;
                case this.props.API_OPTIONS.PATCH_STOCK:
                    this.props.setStockRecordState({
                        updatedData: response.data
                    });
                    this.props.setStockUpdateRecordState({clearData: true}); // clear data for next time
                    this.props.setMessage({
                        message: 'Stock action successful!',
                        messageClass: 'alert alert-success'
                    });
                    break;
                case this.props.API_OPTIONS.ADD_STOCK:
                case this.props.API_OPTIONS.DELETE_STOCK_LINE:
                    this.props.setStockUpdateRecordState({clearData: true}); // clear data for next time
                    this.props.setStockRecordState({
                        stockRecord: {meta: {preserveOrder: true}},
                        apiTrigger: this.props.API_OPTIONS.GET_STOCK
                    });  // sets data to be refreshed & rebuild of table
                    this.props.setMessage({
                        message: 'Stock action successful!',
                        messageClass: 'alert alert-success'
                    });
                    break;
                case this.props.API_OPTIONS.POST_AUTH:
                    if (response.data) {
                        let token = response.data.token;
                        this.props.setSessionStorage({key: 'apiToken', value: token}); // stick token into local browser storage
                        this.props.setSessionStorage({key: 'username', value: requestData.username}); // store username for good measure
                        this.props.authenticate({auth: true}); // set authenticated status
                        this.props.setMessage({
                            message: 'Authentication successful',
                            messageClass: 'alert alert-success'
                        });
                    }
                    else {
                        this.props.setMessage({
                            message: 'An error occurred whilst connecting to the API.',
                            messageClass: 'alert alert-danger'
                        })
                    }
                    break;
                case this.props.API_OPTIONS.PATCH_CHANGE_PW:
                    if (response.data) {
                        this.props.authenticate({auth: false}); // log out
                        this.props.setMessage({
                            message: 'Password changed! Please login using your new credentials.',
                            messageClass: 'alert alert-success'
                        })
                    } else {
                        this.props.setMessage({
                            message: 'An error occurred whilst connecting to the API.',
                            messageClass: 'alert alert-danger'
                        })
                    }
                    break;
                default:
                    this.props.setMessage({
                        message: 'API action has completed ...',
                        messageClass: 'alert alert-success'
                    })
            }
        }
    }

    /*
    render stuff ...
     */

    renderDefault() {
        return (
            <div></div>
        )
    }

    render() {
        return (
            <div>{this.renderDefault()}</div>
        );
    }
}

export default ApiRequest;