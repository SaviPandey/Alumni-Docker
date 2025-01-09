function toggleNotificationPopup() {
    const popup = document.getElementById("notificationPopup");
    popup.classList.toggle("d-none");
    popup.classList.toggle("d-block");

    // Call the API to mark notifications as read when the popup is opened
    if (!popup.classList.contains("d-none")) {
        fetch('/notifications/mark-read', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    console.log(data.message);
                }

                // Reset the notification count to 0
                const notificationCount = document.getElementById("notificationCount");
                notificationCount.textContent = ''; // Clear the count text
                notificationCount.classList.add("d-none"); // Hide the badge
            })
            .catch(error => {
                console.error("Error marking notifications as read:", error);
            });
    }
}

// Fetch notifications on page load
document.addEventListener("DOMContentLoaded", () => {
    fetch('/notifications')
        .then(response => response.json())
        .then(data => {
            const notificationList = document.querySelector("#notificationPopup ul");
            const notificationCount = document.getElementById("notificationCount");

            // Clear previous notifications
            notificationList.innerHTML = "";

            // Populate notifications
            data.notifications.forEach((notification) => {
                const li = document.createElement("li");
                li.className = "py-1 border-bottom";

                // Assuming the notification object has a `message` field
                li.textContent = notification.message;

                notificationList.appendChild(li);
            });

            // Update notification count
            const unreadCount = data.notifications.filter(n => !n.read).length;
            if (unreadCount > 0) {
                notificationCount.textContent = unreadCount;
                notificationCount.classList.remove("d-none");
            } else {
                notificationCount.textContent = ''; // No text when zero
                notificationCount.classList.add("d-none"); // Hide the badge
            }
        })
        .catch(error => {
            console.error("Error fetching notifications:", error);
        });
});
