const items = document.querySelectorAll(".accordion-item h2");
        function toggleAccordion() {
          const itemToggle = this.getAttribute('aria-expanded');
          for (i = 0; i < items.length; i++) {
            items[i].setAttribute('aria-expanded', 'false');
          }
          if (itemToggle == 'false') {
            this.setAttribute('aria-expanded', 'true');
          }
        }
        items.forEach(item => item.addEventListener('click', toggleAccordion));

        function myFunction() {
          const answer=confirm("Are you sure you want to delete the user");
          return answer;
        }
        function myFunction2() {
          const answer=confirm("Are you sure you want to delete the product");
          return answer;
        }

        var elems = document.getElementsByClassName('confirmation');
        var confirmIt = function (e) {
        if (!confirm('Are you sure?')) e.preventDefault();
        };
        for (var i = 0, l = elems.length; i < l; i++) {
        elems[i].addEventListener('click', confirmIt, false);
        }

        $(document).ready(function () {
          $('table.display').DataTable({
            "responsive": true,
   
       });
          $('.dataTables_length').addClass('bs-select');

        });

        let valueDisplays = document.querySelectorAll(".num");
let interval = 400;
valueDisplays.forEach((valueDisplay) => {
  let startValue = 0;
  let endValue = parseInt(valueDisplay.getAttribute("data-val"));
  let duration = Math.floor(interval / endValue);
  let counter = setInterval(function () {
    startValue += 1;
    valueDisplay.textContent = startValue;
    if (startValue == endValue) {
      clearInterval(counter);
    }
  }, duration);
});