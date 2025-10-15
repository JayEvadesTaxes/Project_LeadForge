function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const main = document.querySelector(".main-content");

  if (sidebar.style.width === "200px") {
    sidebar.style.width = "0";
    main.style.marginLeft = "0";
  } else {
    sidebar.style.width = "200px";
    main.style.marginLeft = "200px";
  }
}

