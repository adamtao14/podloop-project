dataBackEnd = {};
followers_count = document.getElementById("followers");
follow_section = document.getElementById("follow_section");
like_button = document.getElementById("like_button");
like_count = document.getElementById("like_count");

async function call_api(api_url) {
  await fetch(api_url)
    .then(function (response) {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok.");
    })
    .then(function (data) {
      Object.entries(data).forEach(([key, value]) => {
        dataBackEnd[key] = value;
      });
    })
    .catch(function (error) {
      console.log("Error:", error.message);
    });
}

async function check_auth() {
  var api_url = "http://127.0.0.1:8000/api/is-authenticated";
  await call_api(api_url);
}

async function get_episode_user_info() {
  var api_url =
    "http://127.0.0.1:8000/api/podcasts/" +
    dataBackEnd["podcast_slug"] +
    "/episode/" +
    dataBackEnd["episode_slug"];
  await call_api(api_url);
}

async function follow() {
  var api_url =
    "http://127.0.0.1:8000/api/podcasts/" +
    dataBackEnd["podcast_slug"] +
    "/follow";
  await call_api(api_url);
  await get_episode_user_info();
  setPage();
}

async function unfollow() {
  var api_url =
    "http://127.0.0.1:8000/api/podcasts/" +
    dataBackEnd["podcast_slug"] +
    "/unfollow";
  await call_api(api_url);
  await get_episode_user_info();
  setPage();
}

async function like() {
  var api_url =
    "http://127.0.0.1:8000/api/podcasts/" +
    dataBackEnd["podcast_slug"] +
    "/episode/" +
    dataBackEnd["episode_slug"] +
    "/like";
  await call_api(api_url);
  await get_episode_user_info();
  setPage();
}

async function dislike() {
  var api_url =
    "http://127.0.0.1:8000/api/podcasts/" +
    dataBackEnd["podcast_slug"] +
    "/episode/" +
    dataBackEnd["episode_slug"] +
    "/dislike";
  await call_api(api_url);
  await get_episode_user_info();
  setPage();
}

async function init(dataFrontEnd) {
  dataBackEnd = dataFrontEnd;
  dataBackEnd["is_authenticated"] = false;
  //I get all the data that i need from the frontend
  await check_auth();
  //i check ig the user is authenticated
  await get_episode_user_info();

  //in both cases i display what is necessary
  setPage();
}

function setPage() {
  if (dataBackEnd["is_authenticated"]) {
    if (dataBackEnd["is_owner"]) {
      follow_element = `<a class="btn btn-sm btn-warning" href="#">Edit</a>`;
    } else if (dataBackEnd["is_following"]) {
      follow_element = `<a class="btn btn-sm btn-danger" href="#" onClick=unfollow()>Unfollow</a>`;
    } else {
      follow_element = `<a class="btn btn-sm btn-success" href="#" onClick=follow()>follow</a>`;
    }

    if (dataBackEnd["is_liked"]) {
      like_element = `<i class="bi bi-hand-thumbs-up-fill text-success" style="cursor:pointer;" onClick=dislike()></i>`;
    } else {
      like_element = `<i class="bi bi-hand-thumbs-up-fill text-light" style="cursor:pointer;" onClick=like()></i>`;
    }
  } else {
    follow_element = `<a class="btn btn-sm btn-warning" href="/login">Login to follow</a>`;
  }
  followers_count.innerHTML = dataBackEnd["followers"] + " Followers";
  like_button.innerHTML = like_element;
  follow_section.innerHTML = follow_element;
  like_count.innerHTML = dataBackEnd["likes"];
}
