const search = document.querySelector('#search');

search.addEventListener('keyup', searchItems);

// Search bar function
function searchItems(e) {
  // convert text to lowercase
  const text = e.target.value.toLowerCase();
  console.log(text);

  const events = document.querySelectorAll('table tbody tr');

  // Loop through each row
  events.forEach(function(event) {
    let found = false;

    // Loop through each cell in the row
    event.querySelectorAll('td').forEach(function(cell) {
      // Check if the cell contains the search text
      if (cell.textContent.toLowerCase().includes(text)) {
        found = true;
      }
    });

    // Display or hide the row based on search result
    if (found) {
      event.style.display = ""; // Display the row
    } else {
      event.style.display = "none"; // Hide the row
    }
  });
}