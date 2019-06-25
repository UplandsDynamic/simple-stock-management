import './css/data-table.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Paginate from './paginate.js';
import React from 'react'

const DataTableNav = ({
    stockRecord = null, handleGetRecords, handleAddRecord, handleSearch, handleStockTake, authMeta = null,
    accountMode, accountModes, getStyles
} = {}) => {
    const { userIsAdmin, authenticated } = authMeta;
    const addRecordButton = (
        <button onClick={() => handleAddRecord({ stockRecord })}
            className={`btn btn-md btn-warning mr-1 `}>
            <FontAwesomeIcon icon={"plus"} /></button>);

    const stockTakeButton = (
        <button onClick={() => handleStockTake()} className={`btn btn-md btn-warning mr-1 `}>
            <FontAwesomeIcon icon={"eye"} />
        </button>
    )
    if (stockRecord && authenticated) {
        return (
            <React.Fragment>
                <div className={'container mb-1'}>
                    <div className={'row nav-row'}>
                        <div className={'col-12'}>
                            <div className={'btn-group float-right'}>
                                <nav className="nav-pagination float-right" aria-label="Table data pages">
                                    <Paginate stockRecord={stockRecord}
                                        handleGetRecords={handleGetRecords}
                                        accountMode={accountMode}
                                        accountModes={accountModes}
                                        getStyles={getStyles}
                                    />
                                </nav>
                            </div>
                        </div>
                    </div>
                    <div className={'d-flex flex-row'}>
                        <div className={'btn-group'}>
                            <button onClick={() => {
                                Object.assign(stockRecord.meta, { page: 1 });
                                handleGetRecords({ stockRecord })
                            }} className={'btn btn-md btn-warning mr-1 '}>
                                <FontAwesomeIcon icon={"sync-alt"} /></button>
                            {userIsAdmin || accountMode === accountModes.STORE ? addRecordButton : ''}
                            {accountMode === accountModes.STORE ? stockTakeButton : ''}
                        </div>
                        <nav className={'search-navigation w-100 flex-shrink'}>
                            <input value={stockRecord.meta.search} placeholder={'Search'}
                                name={'search'} className={'form-control search'}
                                onChange={(e) =>
                                    handleSearch({ stockRecord, term: e.target.value })
                                } />
                        </nav>
                    </div>
                </div>
            </React.Fragment>
        )
    }
    return null;
};

export default DataTableNav;