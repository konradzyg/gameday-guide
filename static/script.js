function updateTeams() {
    const selectedSport = document.getElementById("sport").value;
    $.ajax({
        url: '/get_teams',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ league: selectedSport }),
        success: function(response) {
            const teamSelect = document.getElementById("team");
            teamSelect.innerHTML = '<option value="">Select a team</option>';
            response.teams.forEach(function(team) {
                const option = document.createElement("option");
                option.value = team;
                option.text = team;
                teamSelect.appendChild(option);
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('searchForm').addEventListener('submit', function (event) {
        const sportSelect = document.getElementById('sport');
        const teamSelect = document.getElementById('team');

        let isValid = true; // Flag to determine if the form is valid

        // Clear previous custom validity messages
        sportSelect.setCustomValidity('');
        teamSelect.setCustomValidity('');

        // Check if league is selected
        if (!sportSelect.value) {
            sportSelect.setCustomValidity('Please select a league.');
            isValid = false;
        }

        // Check if team is selected
        if (!teamSelect.value) {
            teamSelect.setCustomValidity('Please select a team.');
            isValid = false;
        }

        // Prevent form submission if validation fails
        if (!isValid) {
            event.preventDefault(); // Prevent form submission
        }
    });
});

