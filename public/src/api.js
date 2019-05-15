import axios from 'axios/index';

const processRequest = ({
                            stockRecord = {}, requestData = null, apiMode = null, csrfToken = null, url = null
                        } = {}) => {
    const {requestType, method} = apiMode;
    if (apiMode && requestType) {
        if (requestType === 'get_stock') {
            return _getStock({stockRecord, csrfToken, requestMethod: method, url})  // returns a promise
        } else if (apiMode.requestType === 'patch_stock') {
            return _updateStock({stockRecord, csrfToken, requestMethod: method, url})  // returns a promise
        } else if (apiMode.requestType === 'patch_stock') {
        } else if (apiMode.requestType === 'add_stock') {
            return _addStock({stockRecord, csrfToken, requestMethod: method, url})  // returns a promise
        } else if (apiMode.requestType === 'delete_stock_line') {
            return _deleteStock({stockRecord, csrfToken, requestMethod: method})
        } else if (apiMode.requestType === 'post_auth' || requestType === 'patch_change_pw') {
            return _auth({csrfToken, requestData, apiMode, requestMethod: method})
        }
    }
    console.log(`
    No API mode, or stock record configuration set. API requested failed.
    Pertinent variable values: requestType=${requestType}; method=${method}`
    );
    return false;
};

const _getSessionStorage = (key) => {
    //return JSON.parse(localStorage.getItem(key));
    return sessionStorage.getItem(key);
};

const _makeRequest = ({
                          stockRecord = null, requestMethod = null, csrfToken = null, requestData = null,
                          url = null, cacheControl = null
                      } = {}) => {
    const CancelToken = axios.CancelToken;
    let cancel;
    // if no requestData passed, see if update data in stock record data. If not, pass empty data to request.
    requestData = requestData ? requestData : stockRecord.data.updateData ? stockRecord.data.updateData : {};
    if (url && requestMethod) {  // make request
        if (cancel !== undefined) {
            cancel();
            console.log('API request cancelled because an existing request was already underway!')
        }
        return axios({
            cancelToken: new CancelToken((c) => cancel = c),
            method: requestMethod,
            url: url,
            responseType: 'json',
            data: requestData,
            //auth: {},
            headers: {
                Authorization: _getSessionStorage('token') ?
                    `Token ${_getSessionStorage('token')}` : null,
                //'cache-control': 'no-cache',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            } // additional headers here
        })
    }
    console.log('API did not send a request')
};


const _getStock = ({stockRecord = null, csrfToken = null, requestMethod = null, url = null} = {}) => {
    if (stockRecord) {
        if (!url) {
            let {pageOrderBy, pageOrderDir, search, limit, page} = stockRecord.meta;
            if (!url) { // constructs request URL, unless pre-defined in paginate.js through api 'next' or 'previous'.
                // build url
                url = `${process.env.REACT_APP_API_DATA_ROUTE}/stock/?limit=${limit}` +
                    `&offset=${(page * limit) - limit}` +
                    `&order_by=${pageOrderDir}${pageOrderBy}&desc=${search}`; // update URL
            }
        }
        return _makeRequest({stockRecord, csrfToken, requestMethod, url})  // returns a promise
    }
    return false
};

const _updateStock = ({stockRecord = null, csrfToken = null, requestMethod = null, url = null} = {}) => {
    // manager's transfer updates
    if ('records' in stockRecord) {
        url =  `${process.env.REACT_APP_API_DATA_ROUTE}/stock/`;
        return _makeRequest({requestData: {...stockRecord}, csrfToken, requestMethod, url})
    } else if (stockRecord) // admin's stock record updates
    { // build url
        url = url ? url : `${process.env.REACT_APP_API_DATA_ROUTE}/stock/${stockRecord.data.updateData.id}/`;
        return _makeRequest({stockRecord, csrfToken, requestMethod, url})
    }
    return false
};

const _addStock = ({stockRecord = null, csrfToken = null, requestMethod = null, url = null} = {}) => {
    if (stockRecord) {
        // build url
        url = url ? url : `${process.env.REACT_APP_API_DATA_ROUTE}/stock/`;
        return _makeRequest({stockRecord, csrfToken, requestMethod, url})
    }
    return false
};

const _deleteStock = ({stockRecord = null, csrfToken = null, requestMethod = null, url = null} = {}) => {
    if (stockRecord) {
        // build url
        url = url ? url : `${process.env.REACT_APP_API_DATA_ROUTE}/stock/${stockRecord.data.updateData.id}/`;
        return _makeRequest({stockRecord, csrfToken, requestMethod, url})
    }
    return false;
};

const _auth = ({requestMethod = null, csrfToken = null, requestData = null, apiMode = null} = {}) => {
    const apiRoute = process.env.REACT_APP_API_ROUTE;
    const loginURL = `${apiRoute}/api-token-auth/`;
    const changePWURL = `${apiRoute}/v1/change-password/${_getSessionStorage('username')}/`;
    const url = apiMode.requestType === 'patch_change_pw' ? changePWURL : loginURL;
    const cacheControl = 'no-cache';
    return _makeRequest({requestMethod, requestData, csrfToken, cacheControl, url: url})
};

export default processRequest;

/*
Note 1:
    Method to generate the request ordering. Returns '' or '-'.
    Reverses ordering if column clicked when already ordered on the same column. Otherwise, defaults to ascending order.
    Note: page always reverts to page 1 IF column clicked to change order on any page other than 1, as new ordering
    is requested from API. Needs to return to page 1 to display the newly requested (differently sorted) pages -
    otherwise the current page would display any data that happened to correspond to that page of newly received data,
    and that wouldn't be expected behaviour.
    Could also add method (& UI link/button/widget) for columns to LOCALLY order/sort presently displayed page data
    (without an API request) if required.
 */