import React from "react";
import "./css/stock-update-modal.css";
import Modal from "react-modal";
import TruckTable from "./truck-table";
import processRequest from "./api";

Modal.setAppElement(document.body);

Modal.defaultStyles.overlay.backgroundColor = "cornflowerblue";
const REGULAR_STYLES = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
    backgroundColor: "#001e00",
    color: "yellow",
    border: "1px solid yellow",
    borderRadius: "7px 7px 7px 7px",
    boxShadow: "-7px -7px 17px 7px #001e00",
    maxWidth: "800px",
    maxHeight: "95%"
  },
  overlay: {
    backgroundColor: "#2a3517"
  }
};

// const DANGER_STYLES = {
//     content: {
//         top: '50%',
//         left: '50%',
//         right: 'auto',
//         bottom: 'auto',
//         marginRight: '-50%',
//         transform: 'translate(-50%, -50%)',
//         backgroundColor: 'darkred',
//         color: 'white',
//         border: '1px solid yellow',
//         borderRadius: '7px 7px 7px 7px',
//         boxShadow: '-7px -7px 17px 7px black',
//         maxWidth: '800px',
//     },
//     overlay: {
//         backgroundColor: 'gold',
//     }
// };

/*
Note: Various ways to style the modal:
- css stylesheets
- inline (as above, set in state (modalStyles))
- default styles (also as above, as used for overlay background color).
For more info. see: https://reactcommunity.org/react-modal/examples/css_classes.html
 */

class TruckModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      modalStyles: REGULAR_STYLES,
      modalIsOpen: this.props.openTruckModal,
      truck: this.props.truck
    };
    // Remember! This binding is necessary to make `this` work in the callback
    this.handleAfterOpenModal = this.handleAfterOpenModal.bind(this);
  }

  componentWillUnmount() {
    console.log("Unmounting truck modal");
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    // set modal open/close state (source of truth in parent component - app.js)
    let newState = {};
    if (nextProps.truck !== prevState.truck) {
      newState.truck = nextProps.truck;
    }
    return { ...newState, modalIsOpen: nextProps.openTruckModal };
  }

  componentDidUpdate() {}

  componentDidMount() {}

  handleAfterOpenModal() {
    // this.subtitle.style.color = 'yellow'
  }

  dispatchTruck() {
    /*
        method to make API request to transfer stock (PATCH request).
         */
    // copy truck obj to work on, by converting to string representation, then back (use JSON obj representation)
    let truck = JSON.parse(JSON.stringify(this.props.truck));
    if (truck.length > 0) {
      try {
        /* if transferring, delete all superfluous fields from the query to prevent auth issues */
        truck.forEach((consignment, index) => {
          let cargo = consignment.cargo;
          truck[index] = {
            id: cargo.id,
            units_to_transfer: cargo.units_to_transfer
          };
        });
        // hit the api
        const apiRequest = processRequest({
          stockRecord: { records: truck },
          apiMode: this.props.apiOptions.PATCH_STOCK
        });
        if (apiRequest) {
          apiRequest
            .then(response => {
              if (response) {
                if (response.status === 200) {
                  this.props.emptyTruck();
                  // update the main table with the new values
                  this.props.openTruckModalHandler({
                    actionCancelled: false,
                    returnedRecords: response.data
                  });
                }
              }
            })
            .catch(error => {
              console.log(`API error: ${error}`);
              this.props.setMessage({
                message: "Transfer failed! The API rejected the request.",
                messageClass: "alert alert-danger"
              });
              this.props.openTruckModalHandler({ actionCancelled: false });
            });
        }
      } catch (err) {
        // allow fall through to return false by default
        console.log(`API error: ${err}`);
        this.props.openTruckModalHandler({ actionCancelled: false });
      }
    }
  }

  render() {
    if (this.props.stockRecord) {
      const dispatchButtonClasses = [
        "btn",
        "btn",
        "btn-warning",
        "m-2",
        "table-btn"
      ];
      if (!this.state.truck.length > 0) {
        dispatchButtonClasses.push("d-none");
      }
      return (
        <Modal
          isOpen={this.state.modalIsOpen}
          onAfterOpen={this.handleAfterOpenModal}
          onRequestClose={this.handleCloseModal}
          style={this.state.modalStyles}
          closeTimeoutMS={250}
          contentLabel="Truck Action"
        >
          <div className="container">
            <div className="row">
              <div className="col-sm">
                <h2 ref={subtitle => (this.subtitle = subtitle)}>Truck</h2>
              </div>
              <TruckTable
                truck={this.state.truck}
                changeUnits={this.props.changeTruckUnits}
              />
              <div className="col-sm modal-button-cell">
                <button
                  className={dispatchButtonClasses.join(" ")}
                  onClick={() => {
                    this.dispatchTruck();
                  }}
                >
                  Request Truck Dispatch!
                </button>
                <button
                  className={"btn btn btn-outline-light close-button"}
                  onClick={() => {
                    this.props.openTruckModalHandler({ actionCancelled: true });
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </Modal>
      );
    }
    return null;
  }
}

export default TruckModal;
