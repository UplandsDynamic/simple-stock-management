import './css/data-table.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react';

const TruckTable = ({ truck, changeUnits }) => {
    if (truck.length > 0) {
        const tableData = truck.map((consignment, index) => {
            const cargo = consignment.cargo;
            const editButtonClasses = ['btn', 'btn-warning'];
            return (
                <tr key={index}>
                    <td>
                        {cargo.sku}
                    </td>
                    <td>
                        {cargo.desc}
                    </td>
                    <td>
                        {cargo.units_to_transfer}
                    </td>
                    <td>
                        <div className={'btn-group'} role={'group'} aria-label={'Quantity buttons'}>
                            <button id={`addButton_${cargo.id}`} onClick={(e) => {
                                e.preventDefault();
                                changeUnits({ consignmentListIndex: index, func: 'add', cargo });
                            }} className={editButtonClasses.join(' ')}>
                                <FontAwesomeIcon icon={"plus-square"} /></button>
                            <button id={`minusButton_${cargo.id}`} onClick={(e) => {
                                e.preventDefault();
                                changeUnits({ consignmentListIndex: index, func: 'minus', cargo });
                            }} className={editButtonClasses.join(' ')}>
                                <FontAwesomeIcon icon={"minus-square"} /></button>
                            <button id={`deleteButton_${cargo.id}`} onClick={(e) => {
                                e.preventDefault();
                                changeUnits({ consignmentListIndex: index, func: 'clear', cargo });
                            }} className={editButtonClasses.join(' ')}>
                                <FontAwesomeIcon icon={"trash-alt"} /></button>
                        </div>
                    </td>
                </tr>
            );
        });
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className="col-sm">
                            <table className={`table stockTable'}
                        table-bordered table-dark table-hover`}>
                                <caption>Truck</caption>
                                <thead>
                                    <tr>
                                        <th scope={'col'}>SKU</th>
                                        <th scope={'col'}>Description</th>
                                        <th scope={'col'}>Units to Transfer</th>
                                        <th scope={'col'}>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {tableData}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        );
    }
    return (
        <React.Fragment>
            <div className={'container'}>
                <div className={'row'}>
                    <div className={'col-12'}>
                        <div>Truck is empty</div>
                    </div>
                </div>
            </div>
        </React.Fragment>
    )
};
export default TruckTable;