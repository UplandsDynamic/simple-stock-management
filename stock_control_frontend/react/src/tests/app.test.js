import React from 'react'
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
// components imported into component being tested
import App from "../app";
import LoginForm from '../loginform.js';
import DataTable from '../data-table.js';
import StockUpdateModal from '../stock-update-modal.js';
import ApiRequest from '../api-request.js';
import Message from '../message.js';
import Footer from '../footer.js';

// mock state

const STATE = {
    stockRecordData: {
        results: [
            {
                id: 1,
                record_updated: '2019-02-06T15:25:16.039720Z',
                owner: 'tester',
                sku: 'NCC-1701-E',
                desc: 'USS Enterprise',
                units_total: 98,
                unit_price: 98.90,
                user_is_admin: true,
                datetime_of_request: '2019-02-08T01:55:10.258338'
            }
        ]
    },
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
    message: 'Test message',
    messageClass: 'alert-warning',
};

const APIOPTIONS = {
    /* used to define available API options in the api-request component */
    GET_STOCK: {method: 'GET', desc: 'request to get stock data'},
    PATCH_STOCK: {method: 'PATCH', desc: 'PATCH request to update stock data'},
    ADD_STOCK: {method: 'POST', desc: 'POST request to add stock data'},
    DELETE_STOCK_LINE: {method: 'DELETE', desc: 'DELETE request to delete stock line'},
    POST_AUTH: {method: 'POST', desc: 'POST request to for authorization'},
    PATCH_CHANGE_PW: {method: 'PATCH', desc: 'PATCH request to for changing password'},
};

// test component renders

describe('App Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(<App/>, div)
    })
});

// test child components render

describe('App Component', () => {
    it('renders the LoginForm wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(LoginForm)).toHaveLength(1)
    })
});

describe('App Component', () => {
    it('renders the Message wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(Message)).toHaveLength(1);
    });

    it('passes all props to Message component', () => {
        const wrapper = shallow(<App/>);
        wrapper.setState({message: 'Test warning', messageClass: 'warning'});  // set state which is passed as props
        let messageWrapper = wrapper.find(Message);
        expect(messageWrapper.props().message).toEqual('Test warning');  // test message displayed with props
        expect(messageWrapper.props().messageClass).toEqual('warning');
    })
});

describe('App Component', () => {
    it('does not render the DataTable wrapper if unauthenticated', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(DataTable)).toHaveLength(0)
    });
    it('does render the DataTable wrapper if authenticated', () => {
        const wrapper = shallow(<App/>);
        wrapper.instance().authenticate({auth: true});  // need instance of component to access component's methods
        expect(wrapper.find(DataTable)).toHaveLength(1)
    });
    it('passes all props to DataTable component', () => {
        const wrapper = shallow(<App/>);
        wrapper.instance().authenticate({auth: true});  // authenticate.  Note: instance() allows access to component's methods
        wrapper.setState(STATE);  // set state which is passed as props
        const dataTableWrapper = wrapper.find(DataTable);
        expect(dataTableWrapper.props().stockRecordData).toEqual(STATE.stockRecordData);
        expect(dataTableWrapper.props().stockRecordMeta).toEqual(STATE.stockRecordMeta);
        expect(dataTableWrapper.props().message).toEqual(STATE.message);
        expect(dataTableWrapper.props().messageClass).toEqual(STATE.messageClass);
        expect(dataTableWrapper.props().apiOptions).toEqual(APIOPTIONS);
        expect(dataTableWrapper.props().setStockRecordState).toBe(wrapper.instance().setStockRecordState);
    })
});

describe('App Component', () => {
    it('does render the StockUpdateModal wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(StockUpdateModal)).toHaveLength(1)
    })
});

describe('App Component', () => {
    it('does render the ApiRequest wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(ApiRequest)).toHaveLength(1)
    })
});

describe('App Component', () => {
    it('does render the Footer wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(Footer)).toHaveLength(1)
    })
});

// test methods

describe('App Component', () => {
    it('method setStockRecordState successfully returns true', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.instance().setStockRecordState()).toBe(true)
    })
});
