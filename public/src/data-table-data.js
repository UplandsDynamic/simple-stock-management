import './css/data-table.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'

const DataTableData = ({ stockRecord = {}, handleEditRecord, accountMode, accountModes,
    formatUTCDateTime, authMeta = {} } = {}) => {
    const { authenticated, userIsAdmin } = authMeta;
    const storeAccount = accountMode === accountModes.STORE
    if (!stockRecord || !authenticated || (stockRecord && stockRecord.data.results.length < 1)) {
        return (
            <React.Fragment>
                <tr data-toggle="modal" className={'d-flex dataTableRows'}>
                    <td className={'col-12 no-data'}>
                        <div className={'alert alert-warning'}>There are no records to display!</div>
                    </td>
                </tr>
            </React.Fragment>
        )
    }
    if (storeAccount) {
        return stockRecord.data.results.map((item, index) => {
            let { sku, desc, units_total, xfer_price, record_updated, shrinkage, sold_units, selling_price } = item;
            let rowClasses = [units_total <= 0 ? 'outOfStock' : '', 'd-flex', 'dataTableRows'];
            let editButtonClasses = ['table-btn', 'btn', 'btn-primary', 'w-100', 'mb-1'];
            return (<tr key={item.id} data-toggle="modal" className={rowClasses.join(' ')}>
                {/*<th scope="row">{item.id}</th>*/}
                <td className={'col-1 sku'}>{sku}</td>
                <td className={'col-2 desc'}>{desc}</td>
                <td className={'col-1 unitsTotal'}>{units_total > 0 ? units_total : 'Out of Stock'}</td>
                <td className={'col-1 shrinkage'}>{shrinkage}</td>
                <td className={'col-1 shrinkage'}>{sold_units}</td>
                <td className={'col-1 unitPrice'}>{xfer_price}</td>
                <td className={'col-1 selling_price'}>{selling_price}</td>
                <td className={'table-small-font col-2 recordUpdated'}>
                    {formatUTCDateTime({ dateTime: record_updated })}</td>
                <td className={'action-col col-2 text-center'}>
                    <button id={`editButton_${item.id}`} onClick={() => {
                        if (userIsAdmin || storeAccount) {
                            Object.assign(stockRecord.data, {
                                updateData: {
                                    ...item, // copy vals, don't pass obj. *see note (1)
                                    resultIndex: index,
                                    start_units_total: units_total
                                }
                            });  // copy vals, don't pass obj
                            // reset shrinkage & sold_units in update_data to 0, as want to submit new values in edits here, not increments
                            stockRecord.data.updateData.shrinkage = 0;
                            stockRecord.data.updateData.sold_units = 0;
                            return handleEditRecord({ stockRecord: stockRecord })
                        } else return null;
                    }} className={editButtonClasses.join(' ')}>
                        <FontAwesomeIcon icon={"edit"} /></button>
                    {userIsAdmin ? <button onClick={() => {
                        // assign record to be deleted to stockRecord.data's updateData value
                        Object.assign(stockRecord.data, { updateData: { ...item, resultIndex: index } });
                        return handleEditRecord({ stockRecord: stockRecord, deleteRecord: true })
                    }}
                        className={'table-btn btn btn-danger w-100'} id={`deleteButton_${item.id}`}>
                        <FontAwesomeIcon icon={"trash-alt"} /></button> : ''}
                </td>
            </tr>)
        });
    }
    else {
        return stockRecord.data.results.map((item, index) => {
            let { sku, desc, units_total, unit_price, record_updated } = item;
            let rowClasses = [units_total <= 0 ? 'outOfStock' : '', 'd-flex', 'dataTableRows'];
            let editButtonClasses = [units_total <= 0 && (!userIsAdmin || !storeAccount) ?
                'disabled' : '', 'table-btn', 'btn', 'btn-primary', 'w-100', 'mb-1'];
            return (<tr key={item.id} data-toggle="modal" className={rowClasses.join(' ')}>
                {/*<th scope="row">{item.id}</th>*/}
                <td className={'col-2 sku'}>{sku}</td>
                <td className={'col-2 desc'}>{desc}</td>
                <td className={'col-2 unitsTotal'}>{units_total > 0 ? units_total : 'Out of Stock'}</td>
                <td className={'col-2 unitPrice'}>{unit_price}</td>
                <td className={'table-small-font col-2 recordUpdated'}>
                    {formatUTCDateTime({ dateTime: record_updated })}</td>
                <td className={'action-col col-2 text-center'}>
                    <button id={`editButton_${item.id}`} onClick={() => {
                        if (userIsAdmin || storeAccount || (!userIsAdmin && units_total > 0)) {
                            Object.assign(stockRecord.data, {
                                updateData: {
                                    ...item, // copy vals, don't pass obj. *see note (1)
                                    resultIndex: index,
                                    start_units_total: units_total
                                }
                            });  // copy vals, don't pass obj
                            return handleEditRecord({ stockRecord: stockRecord })
                        } else return null;
                    }} className={editButtonClasses.join(' ')}>
                        <FontAwesomeIcon icon={"edit"} /></button>
                    {userIsAdmin ? <button onClick={() => {
                        // assign record to be deleted to stockRecord.data's updateData value
                        Object.assign(stockRecord.data, { updateData: { ...item, resultIndex: index } });
                        return handleEditRecord({ stockRecord: stockRecord, deleteRecord: true })
                    }}
                        className={'table-btn btn btn-danger w-100'} id={`deleteButton_${item.id}`}>
                        <FontAwesomeIcon icon={"trash-alt"} /></button> : ''}
                </td>
            </tr>)
        });
    }
};

export default DataTableData;

/*
Note 1: Be sure to pass values (e.g. {...item}) rather than obj (e.g. {item}),
otherwise the item obj (corresponding to the data results on the main table) will be updated with
values input in the console, as data.updateData would essentially
point to data.results, rather than being a separate, discrete object.
 */