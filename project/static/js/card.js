
// list of rows of movies table 
function generate_cards(movies, uid){
		console.log(uid);
		var container = document.getElementById("mycardcontainer");
		movies.forEach((row, idx) => {
			// Create card element
			var card = document.createElement('div');
			card.classList = 'card-body';

			// Construct card content
			var content = `
			<div class="col-sm-4">
				<div class="card o-visible">
					<div class="card-header">
						<h5>${row[2]}</h5>
					</div>
					 <div class="card mat-clr-stat-card text-white blue m-15">
						<div class="card-block">
							<p class="m-b-0">Year: ${row[3]}</p>
							<p class="m-b-0">duration: ${row[4]}min</p>
						</div>
					</div>
					<div class="star-rating rateYo" id=${row[0]}></div>
					<div class="col-9">
						<p class="m-b-0">${row[7]}stars, Average of ${row[6]} ratings</p>
					</div>
				</div>
			</div>`;

			// Append newyly created card element to the container
			container.innerHTML += content;
			// row[0] is movielens_title_id
			$(function () {
				$("#"+row[0]).rateYo({
					rating: row[8],
					onSet: function (rating, rateYoInstance) {
						alert("user "+uid + " rated: movielens_title_id " + row[0] + ' '+ rating);
						var request = {
							movielens_title_id: row[0],
							rating: rating
						}
						$.ajax({
							url: '/rate',
							data: JSON.stringify(request),
							contentType: 'application/json',
							type: 'POST',
							async: false, // this is needed in order to get a proper response from server (server is doing a database query and thus takes long)
							dataType: 'json',
							success: function(response){
								alert(response)
							},
							error: function(jqXHR, textStatus, errorThrown) {
								console.log(textStatus);
								console.log(errorThrown);
								alert(jqXHR.responseText);
							}
						})
					}
				});
			});


		}) 
}