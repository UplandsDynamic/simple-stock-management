import React from "react";
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
import StockUpdateTable from '../stock-update-table';
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare);


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
        authenticated: true,
        userIsAdmin: true,
    },
    stockUpdateModalOpen: false,
    apiMode: mockAPIOptions.GET_STOCK,  // will be one of apiOptions when triggered
    message: null,
    messageClass: '',
    greeting: process.env.REACT_APP_GREETING,
    csrfToken: null
};

const StockUpdateTableWithProps = (<StockUpdateTable
    stockRecord={mockProps.stockRecord}
    authMeta={mockProps.authMeta}
    handleRecordUpdate={jest.fn()}
    handleCloseModal={jest.fn()}
    dataUpdate={jest.fn()}
/>);


// test component renders

describe('StockUpdateTable Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(StockUpdateTableWithProps, div)
    })
});

