import {
  getCookie,
  setCookie
} from "./cookies.js";
import { requestData } from "./request-data.js";

const EMAIL_REGEX = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;

function handleSubscribeInput() {
  const textField = document.querySelector(`.subscribe input`);
  const subscribeButton = document.querySelector(`.subscribe .btn-sm`);
  const text = textField.value;
  if (EMAIL_REGEX.test(text)) {
    // if not disabled, check whether it should be selected or not
    requestData(`/subscribe/check/${text}`, (responseText) => {
      const inList = JSON.parse(responseText);
      subscribeButton.classList.remove(`disabled`);

      if (inList) {
        subscribeButton.classList.add(`selected`);
      } else {
        subscribeButton.classList.remove(`selected`);
      }
    });
  } else {
    subscribeButton.classList.add(`disabled`);
    subscribeButton.classList.remove(`selected`);
  }

  // save state of this input as a cookie
  setCookie(`subscribe-email`, text, { "max-age": 2147483647 })
}

function handleSubscribeToggle() {
  const textField = document.querySelector(`.subscribe input`);
  const subscribeButton = document.querySelector(`.subscribe .btn-sm`);
  const text = textField.value;
  if (EMAIL_REGEX.test(text)) {
    requestData(`/subscribe/toggle/${text}`, () =>
      // reload sub count
      requestData(`/subscribe/count.json`, (responseText) => {
        subscribeButton.classList.toggle(`selected`);
        document.querySelector(`.subscribe .count`)
          .innerHTML = JSON.parse(responseText);
      }));
  }
}

function initHeaderSubscribe() {
  document.querySelector(`.subscribe input`)
    .addEventListener(`input`, handleSubscribeInput);
  document.querySelector(`.subscribe input`)
    .addEventListener(`keypress`, (event) => {
      if (event.key === "Enter") handleSubscribeToggle();
    });
  const subscribeEmailCookie = getCookie(`subscribe-email`);
  if (subscribeEmailCookie !== undefined)
    document.querySelector(`.subscribe input`).value = subscribeEmailCookie;
  handleSubscribeInput();
  document.querySelector(`.subscribe .btn-sm`)
    .addEventListener(`click`, handleSubscribeToggle);
}

initHeaderSubscribe()