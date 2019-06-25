import {configure} from "enzyme/build";
import Adapter from "enzyme-adapter-react-16";
import 'jest-enzyme';

const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};

const sessionStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};

const mockAPIOptions = {
    /* used to define available API options in the api-request component */
    GET_STOCK: {name: 'get_stock', method: 'GET', desc: 'request to get stock data'},
    PATCH_STOCK: {name: 'patch_stock', method: 'PATCH', desc: 'PATCH request to update stock data'},
    ADD_STOCK: {name: 'add_stock', method: 'POST', desc: 'POST request to add stock data'},
    DELETE_STOCK_LINE: {name: 'delete_stock_line', method: 'DELETE', desc: 'DELETE request to delete stock line'},
    POST_AUTH: {name: 'post_auth', method: 'POST', desc: 'POST request to for authorization'},
    PATCH_CHANGE_PW: {name: 'patch_change_pw', method: 'PATCH', desc: 'PATCH request to for changing password'},
};

const mockProps = {
    stockRecord: {
        meta: {
            page: 1,
            limit: 3,
            pagerMainSize: 5,
            pagerEndSize: 3,
            pageOrderBy: '',
            pageOrderDir: '',
            previous: null,
            next: null,
            cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
            search: '',
            newRecord: false,
            deleteRecord: false
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
    updateModalOpen: false,
    apiMode: mockAPIOptions.GET_STOCK,  // will be one of apiOptions when triggered
    message: null,
    messageClass: '',
    greeting: process.env.REACT_APP_GREETING,
    csrfToken: null
};


global.localStorage = localStorageMock;
global.sessionStorage = sessionStorageMock;
global.mockProps = mockProps;
global.mockAPIOptions = mockAPIOptions;

// set enzyme adapter
configure({adapter: new Adapter()});