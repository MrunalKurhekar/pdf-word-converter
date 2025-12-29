import axios from "axios";

const API = axios.create({
  baseURL: "https://pdf-converter-backend-48r9.onrender.com/",
});

export default API;
