import './css/data-table.css';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import React from 'react'

const DataTableData = ({stockRecord = {}, handleEditRecord, handleDeleteLine, formatUTCDateTime, authMeta = {}} = {}) => {
    const {authenticated, userIsAdmin} = authMeta;
    if (!stockRecord || !authenticated || (stockRecord && stockRecord.data.results.length < 1)) {
        return (
            <React.Fragment>
                <tr data-toggle="modal" className={'d-flex dataTableRows'}>
                    <td className={'col-12 no-data'}>
                        <div className={'alert alert-warning'}> Loading data ...</div>
                    </td>
                </tr>
            </React.Fragment>
        )
    }
    return stockRecord.data.results.map((item, index) => {
        let {sku, desc, units_total, unit_price, record_updated} = item;
        let rowClasses = [units_total <= 0 ? 'outOfStock' : '', 'd-flex', 'dataTableRows'];
        let editButtonClasses = [units_total <= 0 && !userIsAdmin ?
            'disabled' : '', 'table-btn', 'btn', 'btn-primary', 'w-100', 'mb-1'];
        return (<tr key={item.id} data-toggle="modal" className={rowClasses.join(' ')}>
            {/*<th scope="row">{item.id}</th>*/}
            <td className={'col-2 sku'}>{sku}</td>
            <td className={'col-2 desc'}>{desc}</td>
            <td className={'col-2 unitsTotal'}>{units_total > 0 ? units_total : 'Out of Stock'}</td>
            <td className={'col-2 unitPrice'}>{unit_price}</td>
            <td className={'table-small-font col-2 recordUpdated'}>
                {formatUTCDateTime({dateTime: record_updated})}</td>
            <td className={'action-col col-2 text-center'}>
                <button id={`editButton_${item.id}`} onClick={() => {
                    if (userIsAdmin || (!userIsAdmin && units_total > 0)) {
                        Object.assign(stockRecord.data, {
                            updateData: {
                                ...item, // copy vals, don't pass obj. *see note (1)
                                resultIndex: index,
                                start_units_total: units_total
                            }
                        });  // copy vals, don't pass obj
                        return handleEditRecord({stockRecord: stockRecord})
                    } else return null;
                }} className={editButtonClasses.join(' ')}>
                    <FontAwesomeIcon icon={"edit"}/></button>
                {userIsAdmin ? <button onClick={() => {
                    Object.assign(stockRecord.data, {
                        updateData: {
                            ...item, // copy vals, don't pass obj. *see note (1)
                            resultIndex: index,
                            start_units_total: units_total
                        }
                    });
                    return handleEditRecord({stockRecord: stockRecord, deleteRecord: true})
                }}
                                       className={'table-btn btn btn-danger w-100'} id={`deleteButton_${item.id}`}>
                    <FontAwesomeIcon icon={"trash-alt"}/></button> : ''}
            </td>
        </tr>)
    });
};

export default DataTableData;

/*
Note 1: Be sure to pass values (e.g. {...item}) rather than obj (e.g. {item}),
otherwise the item obj (corresponding to the data results on the main table) will be updated with
values input in the console, as data.updateData would essentially
point to data.results, rather than being a separate, discrete object.
 */