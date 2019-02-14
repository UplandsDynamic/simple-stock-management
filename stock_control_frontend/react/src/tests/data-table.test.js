import React from 'react'
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
import DataTable from "../data-table";
import cloneDeep from "lodash.clonedeep"

/* mock state */

const initialMockProps = {
    stockRecordData: {
        data: {
            results: [
                {
                    id: 1,
                    record_updated: '2019-02-06T15:25:16.039720Z',
                    owner: 'tester',
                    sku: 'NCC-1701-E',
                    desc: 'USS Enterprise',
                    units_total: '98',
                    unit_price: '98.90',
                    user_is_admin: true,
                    datetime_of_request: '2019-02-08T01:55:10.258338'
                }
            ]
        }
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

let mockProps = {};

const apiOptions = {
    /* used to define available API options in the api-request component */
    GET_STOCK: {method: 'GET', desc: 'request to get stock data'},
    PATCH_STOCK: {method: 'PATCH', desc: 'PATCH request to update stock data'},
    ADD_STOCK: {method: 'POST', desc: 'POST request to add stock data'},
    DELETE_STOCK_LINE: {method: 'DELETE', desc: 'DELETE request to delete stock line'},
    POST_AUTH: {method: 'POST', desc: 'POST request to for authorization'},
    PATCH_CHANGE_PW: {method: 'PATCH', desc: 'PATCH request to for changing password'},
};

const dataTableComponent = <DataTable
    stockRecordData={mockProps.stockRecordData}
    stockRecordMeta={mockProps.stockRecordMeta}
    message={mockProps.message}
    messageClass={mockProps.messageClass}
    apiOptions={apiOptions}
    setStockRecordState={jest.fn()}
    openStockUpdateModalHandler={jest.fn()}
    setMessage={jest.fn((message) => message)}
/>;


/* extra defined mocks function */

const mockGenerateTable = (wrapper) => {
    wrapper.setState({
        dataTable: wrapper.instance().generateTable({
            stockRecordData: mockProps.stockRecordData,
            stockRecordMeta: mockProps.stockRecordMeta
        })
    });
};

const resetMockProps = () => {
    mockProps = cloneDeep(initialMockProps);
};

// test component renders

describe('DataTable Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(dataTableComponent, div)
    })
});

/* test component elements */

// table rows

resetMockProps();

describe('DataTable Component', () => {
    it('renders table rows', () => {
        const wrapper = shallow(dataTableComponent);
        wrapper.setState({
            dataTable: wrapper.instance().generateTable({
                stockRecordData: mockProps.stockRecordData,
                stockRecordMeta: mockProps.stockRecordMeta
            })
        });
        expect(wrapper.find('tr.dataTableRows')).not.toHaveLength(0);
    });
});

// edit button
describe('DataTable Component', () => {
    it('calls handler function when edit button clicked', () => {
        const wrapper = shallow(dataTableComponent);
        const mockHandleEditRecord = jest.spyOn(DataTable.prototype, 'handleEditRecord');
        mockGenerateTable(wrapper);
        wrapper.find('#editButton_1').simulate('click');
        wrapper.update();
        expect(mockHandleEditRecord).toHaveBeenCalled();
        jest.clearAllMocks();
    });
    it('does not call handler if edit button clicked when quantity <= 0 & user not admin', () => {
        const wrapper = shallow(dataTableComponent);
        const mockHandleEditRecord = jest.spyOn(DataTable.prototype, 'handleEditRecord');
        mockProps.stockRecordData.data.results[0].units_total = 0;
        mockGenerateTable(wrapper);
        wrapper.find('#editButton_1').simulate('click');
        wrapper.update();
        expect(mockHandleEditRecord).not.toHaveBeenCalled();
        jest.clearAllMocks();
        resetMockProps()
    });
});

// delete button
describe('DataTable Component', () => {
    it('does not show delete button if user is not admin', () => {
        const wrapper = shallow(dataTableComponent);
        expect(wrapper.find('#deleteButton_1')).toHaveLength(0)
    });
    it('does show delete button if user is admin', () => {
        const wrapper = shallow(dataTableComponent);
        mockProps.stockRecordMeta.userIsAdmin = true;
        mockGenerateTable(wrapper);
        expect(wrapper.find('#deleteButton_1')).toHaveLength(1)
    });
    it('calls handler function when delete button clicked', () => {
        const wrapper = shallow(dataTableComponent);
        const mockHandleDeleteLine = jest.spyOn(DataTable.prototype, 'handleDeleteLine');
        mockGenerateTable(wrapper);
        wrapper.find('#deleteButton_1').simulate('click');
        wrapper.update();
        expect(mockHandleDeleteLine).toHaveBeenCalled();
        jest.clearAllMocks();
    });
});

/* test correct props passed to the table & displayed */

describe('DataTable Component', () => {
    it('displays correct props in data table', () => {
        const wrapper = shallow(dataTableComponent);
        mockProps.stockRecordData.data.results[0].units_total = 0;
        mockGenerateTable(wrapper);
        expect(wrapper.find('td.unitsTotal')).toHaveText('Out of Stock');
        resetMockProps(); // reset mock prop values
        mockGenerateTable(wrapper);
        expect(wrapper.find('td.unitsTotal')).toHaveText('98');
        jest.clearAllMocks();
        resetMockProps(); // reset mock prop values
        expect(wrapper.find('td.sku')).toHaveText('NCC-1701-E');
        expect(wrapper.find('td.desc')).toHaveText('USS Enterprise');
        expect(wrapper.find('td.unitPrice')).toHaveText('98.90');
        expect(wrapper.find('td.recordUpdated')).toHaveText('06/02/2019 15:25:16 GMT');
    });
});

/* test methods & functions */

describe('Component: DataTable', () => {
    it('formats datetime correctly', () => {
        const originalFormat = mockProps.stockRecordData.data.results[0].record_updated;
        expect(DataTable.formatUTCDateTime({dateTime: originalFormat})).toBe('06/02/2019 15:25:16 GMT')
    });
});

describe('Component: DataTable, Method: handleEditRecord', () => {
    it('calls open modal handler with correct arguments', () => {
        const record = {...mockProps.stockRecordData.data.results[0]};
        const wrapper = shallow(dataTableComponent);
        const instance = wrapper.instance();
        const mockOpenStockUpdateModalHandler = jest.spyOn(instance.props, 'openStockUpdateModalHandler');
        instance.handleEditRecord({record: {record}});
        expect(mockOpenStockUpdateModalHandler).toHaveBeenCalledWith({record: {record}})
    });
     it('resets message to null', () => {
        const record = {...mockProps.stockRecordData.data.results[0]};
        const wrapper = shallow(dataTableComponent);
        const instance = wrapper.instance();
        const mockSetMessage = jest.spyOn(instance.props, 'setMessage');
        instance.handleEditRecord({record: {record}});
        expect(mockSetMessage).toHaveBeenCalledWith({message: null})
    });
});