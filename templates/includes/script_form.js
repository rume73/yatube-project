<script>

  function first() {
  
  document.getElementById("form_hide").setAttribute("style", "opacity:1; transition: 1s; height: 100%;");
  
  document.getElementById("first").setAttribute("style", "display: none");
  
  document.getElementById("second").setAttribute("style", "display: block");
  
  }
  
  function second() {
  
  document.getElementById("form_hide").setAttribute("style", "display: none");
  
  document.getElementById("second").setAttribute("style", "display: none");
  
  document.getElementById("first").setAttribute("style", "display: block");
  
  }
  
  </script>