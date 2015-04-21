function SwitchResourcesInput(mode) { 
  var g5k = document.getElementById('grid5000').getElementsByTagName('input')[0];
  if (mode.value=='free') { 
    g5k.setAttribute('type', 'text') 
  } else { 
    g5k.setAttribute('type', 'checkbox')
  }
  var inputs = document.getElementById('elements').getElementsByTagName('input');
  for (var i = 0; i < inputs.length; i++) {
    if (mode.value=='free') { 
      inputs[i].setAttribute('type', 'text') }
    else { 
      inputs[i].setAttribute('type', 'checkbox')}
  } 
  if (mode.value!='date') {
      document.getElementById('end_date_picker').disabled=false;
  } else {
      document.getElementById('end_date_picker').disabled=true;
  }
}

function SwitchSites(g5k) {
  mode = document.getElementById('mode').getElementsByTagName('select')[0].value;
  if (mode != 'free') {
    var sites = document.getElementsByClassName('site');
    if (g5k.checked) {
      for (var i = 0; i < sites.length; i++) {
        sites[i].getElementsByTagName('input')[0].checked = true;
        sites[i].getElementsByTagName('input')[0].disabled = true;
	SwitchSiteClusters(sites[i].getElementsByTagName('input')[0]);
      }
    } else {
      for (var i = 0; i < sites.length; i++) {
        sites[i].getElementsByTagName('input')[0].checked = false;
        sites[i].getElementsByTagName('input')[0].disabled = false;
	SwitchSiteClusters(sites[i].getElementsByTagName('input')[0], true);
      }
    }
  }
}


function SwitchSiteClusters(site, clear) {
  if (mode != 'free') {
    var clusters = document.getElementById(site.name).getElementsByClassName('cluster');

    if (site.checked) {
      for (var i = 0; i < clusters.length; i++) {
        clusters[i].getElementsByTagName('input')[0].checked = true;
	clusters[i].getElementsByTagName('input')[0].disabled = true;
      }	
    } else {
      document.getElementById('grid5000').getElementsByTagName('input')[0].checked=false;      
      for (var i = 0; i < clusters.length; i++) {
        clusters[i].getElementsByTagName('input')[0].disabled = false;
        if (clear || clusters.length == 1) {
          clusters[i].getElementsByTagName('input')[0].checked = false;
        }
      }
    }
  }
}

