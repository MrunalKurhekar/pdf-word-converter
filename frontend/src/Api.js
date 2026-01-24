import axios from "axios";

// const API = axios.create({
//   baseURL: "https://pdf-converter-backend-48r9.onrender.com/",
// });
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

export default API;
