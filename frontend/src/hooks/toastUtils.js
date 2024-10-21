import { ToastContainer, Zoom, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export const showError = (message) => {
  toast.error(message);
};

export const showSuccess = (message) => {
  toast.success(message);
};

export const showAlert = (message) => {
  toast.warning(message);
};
