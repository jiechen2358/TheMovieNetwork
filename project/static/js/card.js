
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
				<form id="ratingForm">
					<fieldset class="rating">
						<p>Please rate:</p>
						<input type="radio" id="star5" name="rating" value="5" /><label for="star5" title="Rocks!">5 stars</label>
						<input type="radio" id="star4" name="rating" value="4" /><label for="star4" title="Pretty good">4 stars</label>
						<input type="radio" id="star3" name="rating" value="3" /><label for="star3" title="Meh">3 stars</label>
						<input type="radio" id="star2" name="rating" value="2" /><label for="star2" title="Kinda bad">2 stars</label>
						<input type="radio" id="star1" name="rating" value="1" /><label for="star1" title="Sucks big time">1 star</label>
					</fieldset>
					<div class="clearfix"></div>
					<button class="submit clearfix">Submit</button>
				</form>
				<div class="col-9">
					<p class="m-b-0">${row[7]}stars, Average of ${row[6]} ratings</p>
				</div>
			</div>
			<!-- popover card end -->
			</div>`;
			

		// Append newyly created card element to the container
		container.innerHTML += content;
		}) 
}