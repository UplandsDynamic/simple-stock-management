/*global mockProps*/
import React from 'react'
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
import DataTable from "../data-table";
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit
} from '@fortawesome/free-solid-svg-icons'
import StockUpdateModal from "../app";

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare);

const StockUpdateModalWithProps = (
    <StockUpdateModal
        stockRecord={mockProps.stockRecord}
        authMeta={mockProps.authMeta}
        openStockUpdateModal={mockProps.updateModalOpen}
        apiOptions={mockProps.apiOptions}
        apiMode={mockProps.apiMode}
        setStockUpdateModalState={jest.fn()}
        setStockRecordState={jest.fn()}
        setMessage={jest.fn()}
    />
);

// test component renders

describe('DataTable Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(StockUpdateModalWithProps, div)
    })
});