// are we on https?
const isHttps = window.location.protocol === "https:";

function keepOnly(obj, keys) {
  let newObj = {};

  for (let key of keys) {
    newObj[key] = obj[key];
  }

  return newObj;
}

class ApiClient {
  async beforeSendResponse(resp) {
    return resp;
  }

  async request(method, endpoint, options = {}) {
    options.method = method;

    endpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

    const token = localStorage.getItem(this.tokenName);

    let add_header = token ? { Authorization: token } : {};

    options.headers = options.headers
      ? { ...options.headers, ...add_header }
      : add_header;

    const resp = await fetch(`${this.baseUrl}${endpoint}`, options);

    return await this.beforeSendResponse(resp);
  }

  async get(endpoint, options = {}) {
    return this.request("GET", endpoint, options);
  }

  async post(endpoint, body = {}, options = {}) {
    options.body = body ? JSON.stringify(body) : options.body;

    return this.request("POST", endpoint, options);
  }
}

class PipesApi extends ApiClient {
  baseUrl = isHttps ? "https://m.nirush.me" : "http://192.168.50.73:6969";
  tokenName = "pipesToken";

  async redirectToLogin() {
    // make sure the server is alive first
    const url = `${this.baseUrl}/health`;


    try {
      await fetch(url);
    } catch (e) {
      return "down";
    }

    // server is up
    window.location.href = `${this.baseUrl}/oauth2/connect`;
  }

  async beforeSendResponse(resp) {
    let js = await resp.json();
    console.log(js);

    if (js.error === "unauthorized") {
      localStorage.removeItem("token");
      this.redirectToLogin();
      return;
    }

    return js;
  }

  // methods
  async getPipes() {
    return await this.get("/pipes");
  }

  async addPipe(data) {
    return await this.post("/add_pipe", data);
  }

  async editPipe(data) {
    let keep = ["id", "description", "webhook_url", "hmac_header", "hmac_secret"];
    data = keepOnly(data, keep);

    return await this.post("/edit_pipe", data);
  }

  async deletePipe(data) {
    return await this.post("/delete_pipe", { id: data.id });
  }
}

// some other file does "import { ApiClient } from './api.js'", so:
export { PipesApi };
