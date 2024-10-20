import { createStore } from "redux";

const savedUser = localStorage.getItem("user");
const initialState = {
  user: savedUser ? JSON.parse(savedUser) : null,
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case "SET_USER":
      localStorage.setItem("user", JSON.stringify(action.payload));
      return {
        ...state,
        user: action.payload,
      };
    case "CLEAR_USER":
      localStorage.removeItem("user");
      return {
        ...state,
        user: null,
      };
    default:
      return state;
  }
};

const store = createStore(reducer);

export default store;
