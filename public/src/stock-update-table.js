import "./css/data-table.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";

const StockUpdateTable = ({
  stockRecord = null,
  authMeta = null,
  handleRecordUpdate,
  dataUpdate,
  newRecord = false,
  accountModes,
  accountMode
} = {}) => {
  let {
    units_total = 0,
    desc = "",
    unit_price = 0,
    sku = "",
    units_to_transfer = 0,
    start_units_total = 0,
    xfer_price = 0,
    selling_price = 0,
    shrinkage = 0,
    sold_units = 0
  } = stockRecord.data.updateData;
  const { userIsAdmin } = authMeta;
  // const to disable edit button if user not admin or it's a new record
  const managerTransfer = !(userIsAdmin || newRecord);
  const storeAccount = accountMode === accountModes.STORE;
  const getStyles = ({ id = "stockTable" } = {}) => {
    if (accountMode === accountModes.STORE) {
      if (id === "stockTable") {
        return { backgroundColor: "#000033", color: "yellow"};
      }
    }
  };

  const handleEnterKey = e => {
    if (e.keyCode === 13) {
      /* e.preventDefault() required to prevent registering "Enter" and
             and submitting the form twice. Does not register first time if not
             explicitly testing for keycode, as onChange does not record
             "Enter" as a keystroke, however testing onKeyDown does.
             */
      e.preventDefault();
      handleRecordUpdate({
        adminUpdate: !managerTransfer,
        accountMode,
        accountModes,
        newRecord
      }); // submit immediately if Enter pressed
    }
  };

  // true|false. Disable submit if input for units was blank
  let disableButton =
    parseInt(units_total) < 0 ||
    (!userIsAdmin && units_to_transfer === 0 && !storeAccount);

  const validatePrice = value => {
    return /^[\d]*[.]?[\d]{0,2}$/.test(value) ? value : unit_price;
  };

  const validateDesc = value => {
    return /^[a-zA-Z\d.\- ]*$/.test(value) ? value : desc;
  };

  if (storeAccount) {
    return (
      <div className={"container"}>
        <div className={"row"}>
          <div className="col-sm">
            <table
              className={`table stockTable table-bordered table-dark table-hover`}
            >
              <caption>Stock Line Record</caption>
              <thead style={getStyles({ id: "stockTable" })}>
                <tr>
                  <th scope={"col"}>Stock Attribute</th>
                  <th scope={"col"}>Value</th>
                </tr>
              </thead>
              <tbody style={getStyles({ id: "stockTable" })}>
                <tr>
                  <th scope={"row"}>
                    <label>SKU</label>
                  </th>
                  <td>
                    <input
                      value={sku}
                      name={"sku"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: { sku: e.target.value }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={!newRecord}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Description</label>
                  </th>
                  <td>
                    <input
                      value={desc}
                      name={"description"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: { desc: validateDesc(e.target.value) }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={!newRecord}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Stock quantity</label>
                  </th>
                  <td>
                    <input
                      value={units_total}
                      name={"quantity"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e => {
                        if (parseInt(e.target.value) >= 0) {
                          return dataUpdate({
                            stockRecord,
                            updated: {
                              units_total: parseInt(e.target.value)
                            }
                          });
                        }
                        return dataUpdate({
                          stockRecord,
                          updated: { units_total: "" }
                        });
                      }}
                      className={"form-control"}
                      type={"text"}
                      disabled={!(!shrinkage && !sold_units)}
                      autoFocus={true}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>New shrinkage</label>
                  </th>
                  <td>
                    <input
                      value={shrinkage || ""}
                      name={"shrinkage"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e => {
                        if (parseInt(e.target.value) > 0) {
                          return dataUpdate({
                            stockRecord,
                            updated: {
                              shrinkage: parseInt(e.target.value)
                            }
                          });
                        }
                        return dataUpdate({
                          stockRecord,
                          updated: { shrinkage: 0 }
                        });
                      }}
                      className={"form-control"}
                      type={"text"}
                      disabled={!(units_total === start_units_total)}
                      autoFocus={false}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>New recorded sales</label>
                  </th>
                  <td>
                    <input
                      value={sold_units || ""}
                      name={"sold_units"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e => {
                        if (parseInt(e.target.value) > 0) {
                          return dataUpdate({
                            stockRecord,
                            updated: {
                              sold_units: parseInt(e.target.value)
                            }
                          });
                        }
                        return dataUpdate({
                          stockRecord,
                          updated: { sold_units: 0 }
                        });
                      }}
                      className={"form-control"}
                      type={"text"}
                      disabled={!(units_total === start_units_total)}
                      autoFocus={false}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Xfer price</label>
                  </th>
                  <td>
                    <input
                      value={xfer_price}
                      name={"xfer-price"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: {
                            xfer_price: validatePrice(e.target.value)
                          }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={!newRecord}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Selling price</label>
                  </th>
                  <td>
                    <input
                      value={selling_price}
                      name={"selling_price"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: {
                            selling_price: validatePrice(e.target.value)
                          }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={false}
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div className={"row"}>
          <div className={"col-sm xfer-button"}>
            <button
              onClick={e => {
                if (!disableButton) {
                  e.preventDefault();
                  handleRecordUpdate({
                    adminUpdate: !managerTransfer,
                    accountMode,
                    accountModes,
                    newRecord
                  });
                }
              }}
              className={"btn btn-lg btn-warning stockActionButton pull-right"}
              disabled={disableButton}
            >
              {newRecord ? "New Stock Item" : "Amend Record"}
            </button>
          </div>
        </div>
      </div>
    );
  } else {
    return (
      <div className={"container"}>
        <div className={"row"}>
          <div className="col-sm">
            <table
              className={`table stockTable${managerTransfer ? "-disabled" : ""}
                        table-bordered table-dark table-hover`}
            >
              <caption>Current Record</caption>
              <thead>
                <tr>
                  <th scope={"col"}>Stock Attribute</th>
                  <th scope={"col"}>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope={"row"}>
                    <label>SKU</label>
                  </th>
                  <td>
                    <input
                      value={sku}
                      name={"sku"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: { sku: e.target.value }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={managerTransfer}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Description</label>
                  </th>
                  <td>
                    <input
                      value={desc}
                      name={"description"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: { desc: validateDesc(e.target.value) }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={managerTransfer}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Warehouse quantity</label>
                  </th>
                  <td>
                    <input
                      value={!managerTransfer ? units_total : start_units_total}
                      name={"quantity"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e => {
                        if (parseInt(e.target.value) >= 0) {
                          return dataUpdate({
                            stockRecord,
                            updated: {
                              units_total: parseInt(e.target.value)
                            }
                          });
                        }
                        return dataUpdate({
                          stockRecord,
                          updated: { units_total: "" }
                        });
                      }}
                      className={"form-control"}
                      type={"text"}
                      disabled={managerTransfer}
                      autoFocus={true}
                    />
                  </td>
                </tr>
                <tr>
                  <th scope={"row"}>
                    <label>Unit price</label>
                  </th>
                  <td>
                    <input
                      value={unit_price}
                      name={"unit-price"}
                      onKeyDown={e =>
                        !disableButton ? handleEnterKey(e) : null
                      }
                      onChange={e =>
                        dataUpdate({
                          stockRecord,
                          updated: {
                            unit_price: validatePrice(e.target.value)
                          }
                        })
                      }
                      className={"form-control"}
                      type={"text"}
                      disabled={managerTransfer}
                    />
                  </td>
                </tr>
              </tbody>
            </table>
            <div className={!managerTransfer ? "d-none" : "row transfer"}>
              <div className={"col-sm"}>Units to Transfer</div>
              <div className={"col-sm"}>
                <input
                  value={units_to_transfer}
                  name={"quantity"}
                  onKeyDown={e => (!disableButton ? handleEnterKey(e) : null)}
                  onChange={e => {
                    let val = parseInt(e.target.value);
                    if (val > 0 && val <= start_units_total) {
                      return dataUpdate({
                        stockRecord,
                        updated: {
                          units_to_transfer: val,
                          units_total: start_units_total - val
                        }
                      });
                    }
                    return dataUpdate({
                      stockRecord,
                      updated: {
                        units_to_transfer: "",
                        units_total
                      }
                    });
                  }}
                  className={"form-control"}
                  autoFocus={true}
                />
              </div>
              <div className={"col-sm"}>
                <div
                  className={"btn-group"}
                  role={"group"}
                  aria-label={"Quantity buttons"}
                >
                  <button
                    className={"btn btn-lg btn-warning"}
                    onClick={() => {
                      if (units_total > 0) {
                        dataUpdate({
                          stockRecord,
                          updated: {
                            units_to_transfer: units_to_transfer + 1,
                            units_total: units_total - 1
                          }
                        });
                      }
                    }}
                  >
                    <FontAwesomeIcon icon={"plus-square"} />
                  </button>
                  <button
                    className={"btn btn-lg btn-warning"}
                    onClick={() => {
                      if (units_total >= 0 && units_total < start_units_total) {
                        dataUpdate({
                          stockRecord,
                          updated: {
                            units_to_transfer: units_to_transfer - 1,
                            units_total: units_total + 1
                          }
                        });
                      }
                    }}
                  >
                    <FontAwesomeIcon icon={"minus-square"} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={"row"}>
          <div className={"col-sm xfer-button"}>
            <button
              onClick={e => {
                if (!disableButton) {
                  e.preventDefault();
                  handleRecordUpdate({
                    adminUpdate: !managerTransfer,
                    accountMode,
                    accountModes,
                    newRecord
                  });
                }
              }}
              className={"btn btn-lg btn-warning stockActionButton pull-right"}
              disabled={disableButton}
            >
              {newRecord
                ? "New Stock Item"
                : managerTransfer
                ? "Load Truck"
                : "Edit Stock Record"}
            </button>
          </div>
        </div>
      </div>
    );
  }
};

export default StockUpdateTable;
