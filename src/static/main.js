const search = document.querySelector('#search');
const sportFilter = document.querySelector('#sport-filter');
const numPlayersFilter = document.querySelector('#num-players-filter')
const levelFilter = document.querySelector('#level-filter');
const locationFilter = document.querySelector('#location-filter')

search.addEventListener('keyup', searchItems);
sportFilter.addEventListener('change', filterEvents);
numPlayersFilter.addEventListener('change', filterEvents)
levelFilter.addEventListener('change', filterEvents);
locationFilter.addEventListener('change', filterEvents)

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

// Events filter function
 function filterEvents() {
  const searchText = search.value.toLowerCase();
  const selectedSport = sportFilter.value.toLowerCase();
  const selectedPlayers = numPlayersFilter.value.toLowerCase();
  const selectedLevel = levelFilter.value.toLowerCase();
  const selectedLocation = locationFilter.value.toLowerCase();

  const events = document.querySelectorAll('table tbody tr');

  // Loop through each row
  events.forEach(function(event) {
    let showEvent = true;

    // Check if the event matches any filter criteria
    if (
      (!event.querySelector('td:nth-child(1)').textContent.toLowerCase().includes(searchText)) ||
      (selectedSport !== 'all' && !event.querySelector('td:nth-child(2)').textContent.toLowerCase().includes(selectedSport)) ||
      (selectedPlayers !== 'all' && !event.querySelector('td:nth-child(3)').textContent.toLowerCase().includes(selectedPlayers)) ||
      (selectedLevel !== 'all' && !event.querySelector('td:nth-child(4)').textContent.toLowerCase().includes(selectedLevel)) ||
      (selectedLocation !== 'all' && !event.querySelector('td:nth-child(5)').textContent.toLowerCase().includes(selectedLocation))
    ) {
      showEvent = false;
    }

    // Display or hide the row based on filter criteria
    if (showEvent) {
      event.style.display = ""; // Display the row
    } else {
      event.style.display = "none"; // Hide the row
    }
  });
}

