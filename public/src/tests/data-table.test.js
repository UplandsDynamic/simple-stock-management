/* global mockProps */
import React from 'react'
import ReactDOM from 'react-dom'
import {mount, render, shallow, configure} from 'enzyme';
import DataTable from "../data-table";
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare);

const DataTableWithProps = (<DataTable stockRecord={mockProps.stockRecord}
                                       apiOptions={mockProps.apiOptions}
                                       authMeta={mockProps.authMeta}
                                       setMessage={jest.fn()}
                                       openStockUpdateModalHandler={jest.fn()}
                                       getReccordsHandler={jest.fn()}/>);

// test component renders

describe('DataTable Component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        ReactDOM.render(DataTableWithProps, div)
    })
});