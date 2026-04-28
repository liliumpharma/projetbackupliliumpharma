(function($) {
    $(document).ready(function() {
        var wilayaField = $('#id_wilaya');
        var communeField = $('#id_commune');

        // This function handles the API call and updating the dropdown
        function fetchAndPopulateCommunes(wilayaId, communeIdToSelect) {
            // Clear the dropdown immediately so old options vanish
            communeField.empty().append('<option value="">---------</option>');
            communeField.trigger('change');

            if (wilayaId) {
                var apiUrl = '/medecins/ajax/communes/?wilaya=' + wilayaId;

                $.getJSON(apiUrl, function(data) {
                    $.each(data, function(index, item) {
                        var option = $('<option></option>').attr('value', item.id).text(item.nom);
                        communeField.append(option);
                    });
                    
                    // MAGIC STEP: If we passed a saved commune ID, select it now!
                    if (communeIdToSelect) {
                        communeField.val(communeIdToSelect);
                    }
                    
                    // Notify Select2 to update the visual UI with the new options/selection
                    communeField.trigger('change');
                    
                }).fail(function(jqxhr, textStatus, error) {
                    console.error("API Error: ", textStatus, error);
                    alert("Error fetching communes. Please check the Developer Tools Network tab.");
                });
            }
        }

        // --- 1. INITIAL PAGE LOAD (When editing an existing Medecin) ---
        var initialWilaya = wilayaField.val();
        
        // Django renders the currently saved commune inside the HTML on page load. 
        // We capture its ID right now before we overwrite the dropdown.
        var initialCommune = communeField.val(); 

        if (initialWilaya) {
            // We have a Wilaya! Fetch its communes and pre-select the saved one.
            fetchAndPopulateCommunes(initialWilaya, initialCommune);
        } else {
            // If adding a brand NEW medecin, clear the Commune dropdown so it doesn't show ALL communes in Algeria
            communeField.empty().append('<option value="">---------</option>');
            communeField.trigger('change');
        }


        // --- 2. MANUAL USER CHANGE (When someone clicks a new Wilaya) ---
        wilayaField.change(function() {
            var newWilayaId = $(this).val();
            
            // We pass 'null' for the commune here because the Wilaya changed, 
            // meaning their old Commune is no longer valid. They must pick a new one.
            fetchAndPopulateCommunes(newWilayaId, null);
        });
        
    });
})(django.jQuery);