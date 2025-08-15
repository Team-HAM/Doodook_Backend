// firebase-messaging-sw.js

// Firebase SDK v8 스타일 불러오기
importScripts("https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js");
importScripts(
  "https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js"
);

// Firebase 설정 (firebaseConfig는 get-fcm-token.html과 동일하게)
// Firebase 설정 (firebaseConfig 동일하게 넣기)
firebase.initializeApp({
  apiKey: "--",
  authDomain: "--",
  projectId: "--",
  storageBucket: "--",
  messagingSenderId: "--",
  appId: "--",
});

// Messaging 객체 생성
const messaging = firebase.messaging();

// 백그라운드 메시지 처리
messaging.onBackgroundMessage(function (payload) {
  console.log(
    "[firebase-messaging-sw.js] Received background message ",
    payload
  );

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
