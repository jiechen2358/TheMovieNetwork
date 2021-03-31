
function generate_cards(movies){
		console.log(movies);
		var container = document.getElementById("mycardcontainer");
		console.log(container);
		movies.forEach((row, idx) => {
			// Create card element
			var card = document.createElement('div');
			card.classList = 'card-body';

			// Construct card content
			var content = `
			<div class="col-sm-4">
			<!-- popover card start -->
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
			<!-- popover card end -->
			</div>`;
			
			// Append newyly created card element to the container
			container.innerHTML += content;
			$(function () {
				$("#"+row[0]).rateYo({
				    onSet: function (rating, rateYoInstance) {
	      					alert("Rating is set to: " + rating);
	      				}
				});
			});


		}) 
}