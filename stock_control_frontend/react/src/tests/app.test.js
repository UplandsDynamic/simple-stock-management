import React from 'react'
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
// components imported into component being tested
import App from "../app";
import LoginForm from '../loginform.js';
import DataTable from '../data-table.js';
import StockUpdateModal from '../stock-update-modal.js';
import Message from '../message.js';
import Footer from '../footer.js';

// test component renders

describe('App Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(<App/>, div);
    })
});

// test child components render

describe('App Component', () => {
    it('renders the LoginForm wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(LoginForm)).toHaveLength(1)
    });
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
    it('does render the DataTable wrapper', () => {
        const wrapper = shallow(<App/>);
        const instance = wrapper.instance();  // instance of the component
        // authenticate
        sessionStorage.setItem('token', 'TEST_TOKEN');
        instance.setAuthentication();
        expect(wrapper.find(DataTable)).toHaveLength(1)
        sessionStorage.clear()  // clean up
    });
    it('passes all props to DataTable component', () => {
        const wrapper = shallow(<App/>);
        const instance = wrapper.instance();
        // authenticate
        sessionStorage.setItem('token', 'TEST_TOKEN');
        instance.setAuthentication();
        const dataTableWrapper = wrapper.find(DataTable);
        expect(dataTableWrapper.props().stockRecordData).toEqual(instance.state.stockRecordData);
        expect(dataTableWrapper.props().stockRecordMeta).toEqual(instance.state.stockRecordMeta);
        expect(dataTableWrapper.props().apiOptions).toEqual(instance.apiOptions);
        expect(dataTableWrapper.props().setStockRecordState).toBe(instance.setStockRecordState);
        expect(dataTableWrapper.props().setMessage).toBe(instance.setMessage);
    });
    sessionStorage.clear()  // clean up
});

describe('App Component', () => {
    it('does render the StockUpdateModal wrapper', () => {
        const wrapper = shallow(<App/>);
        expect(wrapper.find(StockUpdateModal)).toHaveLength(1)
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
    it('method setStockRecordState successfully changes state', () => {
        const wrapper = shallow(<App/>);
        const instance = wrapper.instance();
        instance.setStockRecordState({newStockRecord: {meta: {page: 11}, data: {results: [{user_is_admin: true}]}}});
        expect(instance.state.stockRecord.meta.page).toEqual(11)
    });
    it('method setStockRecordState successfully changes userIsAdmin', () => {
        const wrapper = shallow(<App/>);
        const instance = wrapper.instance();
        instance.setStockRecordState({newStockRecord: {meta: {page: 1}, data: {results: [{user_is_admin: true}]}}});
        expect(instance.state.authMeta.userIsAdmin).toEqual(true);
        instance.setState({authMeta: {userIsAdmin: false}})  // cleanup
    });
    it('method setAuthenticated attempts to retrieve token from session storage', () => {
        const wrapper = shallow(<App/>);
        const instance = wrapper.instance();
        jest.spyOn(Storage.prototype, 'getItem');  // set up spy on storage
        instance.setAuthentication();
        expect(sessionStorage.getItem).toBeCalledWith('token');
        jest.clearAllMocks();
    });
    it('method setAuthenticated successfully sets state.authMeta.authenticated to true if session token exists',
        () => {
            const wrapper = shallow(<App/>);
            const instance = wrapper.instance();
            sessionStorage.setItem('token', 'TEST_TOKEN');
            instance.setAuthentication();
            expect(instance.state.authMeta.authenticated).toEqual(true);
            sessionStorage.clear()  // clean up
        });
    it('method setAuthenticated successfully sets state.authMeta.authenticated to false if no "token" in session',
        () => {
            const wrapper = shallow(<App/>);
            const instance = wrapper.instance();
            instance.setAuthentication();
            expect(instance.state.authMeta.authenticated).toEqual(false);
            sessionStorage.clear()  // clean up
        });
});
