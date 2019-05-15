import './css/data-table.css';
import React from 'react'

const DataTableHead = ({handleColumnOrderChange, stockRecord} = {}) => {
        return (
            <tr className={'d-flex text-center'}>
                <th className={'col-2'} scope={'col'}
                    onClick={() => handleColumnOrderChange({stockRecord, newOrder: 'sku'})}>
                    SKU
                </th>
                <th className={'col-2'} scope={'col'}
                    onClick={() => handleColumnOrderChange({stockRecord, newOrder: 'desc'})}>
                    Description
                </th>
                <th className={'col-2'} scope={'col'}
                    onClick={() => handleColumnOrderChange({stockRecord, newOrder: 'units_total'})}>
                    Units
                </th>
                <th className={'col-2'} scope={'col'}
                    onClick={() => handleColumnOrderChange({stockRecord, newOrder: 'unit_price'})}>
                    Unit Price
                </th>
                <th className={'col-2'} scope={'col'} onClick={() => handleColumnOrderChange({
                    stockRecord,
                    newOrder: 'record_updated'
                })}>
                    Record Updated
                </th>
                <th className={'col-2 action-col'} scope={'col'}>
                    Action
                </th>
            </tr>
        )
    }
;

export default DataTableHead;