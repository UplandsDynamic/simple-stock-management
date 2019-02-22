import React from "react";
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
import StockUpdateTable from '../stock-update-table';
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit
} from '@fortawesome/free-solid-svg-icons'
import StockUpdateModal from "../app";

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare);

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