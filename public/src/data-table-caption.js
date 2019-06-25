import './css/data-table.css';
import React from 'react'

const DataTableCaption = ({ stockRecord, accountMode, accountModes, _formatUTCDateTime } = {}) => {
    if (accountMode === accountModes.WAREHOUSE) {
        return (
            <caption>{process.env.REACT_APP_SHORT_ORG_NAME} Warehouse Stock Data
            {stockRecord.meta.datetime_of_request ?
                    `[Request returned:
                        ${_formatUTCDateTime({
                        dateTime: stockRecord.meta.datetime_of_request
                    })}]` : ''}
            </caption>
        )
    } else if (accountMode === accountModes.STORE) {
        return (
            <caption>{process.env.REACT_APP_SHORT_ORG_NAME} Account Stock Data
            {stockRecord.meta.datetime_of_request ?
                    `[Request returned:
                        ${_formatUTCDateTime({
                        dateTime: stockRecord.meta.datetime_of_request
                    })}]` : ''}
            </caption>
        )
    }
}
export default DataTableCaption;