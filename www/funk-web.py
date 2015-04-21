#!/usr/bin/env python


import cgi
from pprint import pprint

from execo_g5k import get_g5k_sites, get_site_clusters




def get_all_form_values():
    """//Get the values from all web forms using the HTTP GET method//

    - Arguments:
    
    - The function returns the form content     

    - Note: Special HTML character are escaped before being returned by this function
        
    """
    form=cgi.FieldStorage()
    print form
    res={}
    for k in form:
        v=form.getvalue(k)
        if v is None:
            res[k]=None
        else:
            res[k]=cgi.escape(v)
    
    return res

def get_form_value(name='funk_request'):
    """ """
    if not isinstance(name, str):
        log.error("The name argument must be a string !")
        return None      
            
            
    form=cgi.FieldStorage()
    v=form.getvalue(name)
    
    if v is None:
        return None
    else:
        return cgi.escape(v)


def print_header():
    """ """
    print 'Content-type: text/html'
    print 
    

def print_form():
    """ """
    html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <link href="static/reset.css" rel="stylesheet" media="all" type="text/css">
  <link href="static/main.css" rel="stylesheet" media="all" type="text/css">
  <script type="text/javascript" src="static/main.js"></script>
</head>
<body>
  <div id="main">
    <h1>Funk</h1>
    <form name="funk_request" method="get">
    <div id="general">
      <h2 class="div_head">General</h2>
      <div id="mode">
        <span title="How do you want your nodes ?">Mode</span>    
        <select onchange="SwitchResourcesInput(this)">
          <option value="date">Date - give you the number of nodes available at a given date</option>
          <option value="free">Free - find the next free slot for a combination of resources</option>
          <option value="max">Max - find the time slot where the maximum number of nodes are available</option>
        </select>
      </div>  
      <div id="autoresa">
        <span title="Perform reservation at the end of the execution">Autoreservation</span> 
        <input type="checkbox" name="auto"/>
      </div>
    </div>
    <div id="time">
      <h2 class="div_head">Time</h2>
      <div id="walltime">
        <span title="Can be OAR format 1:00:00 or seconds">Walltime</span> 
        <input class="easyui-timespinner" id="walltime_picker" style="width:80px;"
            data-options="showSeconds:true">
      </div>
      <div id="start">
        <span title="type or pick start date and time">Start</span> 
        <input class="date_picker" type="text" id="start_date_picker">
      </div>
      <div id="end">
        <span title="type or pick end date and time">End</span>
        <input class="date_picker" type="text" id="end_date_picker" disabled="true">
      </div>
      <div id="charter">
        <span title="e.g run only night/week-end">Avoid charter periods </span> 
        <input type="checkbox">
      </div>
    </div>
    <div id="nodes">
      <h2 class="div_head">Nodes</h2>
      <div id="grid5000">    
        <input type="checkbox" name="grid5000" onclick="SwitchSites(this)"/> Use any nodes on Grid'5000 
      </div>
    </div>
    <div id="elements">\n"""
    for site in sorted(get_g5k_sites()):
        html += "        <div id=\"" + site + "\" class=\"site\">\n" + \
            "          <input type=\"checkbox\" name=\"" + site + "\" onclick=\"SwitchSiteClusters(this)\"/>" + \
            "\n          <span>" + site + "</span>\n"        
        for cluster in sorted(get_site_clusters(site)):
            html += "          <div id=\"" + cluster + "\" class=\"cluster\">\n" + \
                "            <input type=\"checkbox\" name=\"" + cluster + "\"/>\n            <span>" + cluster + "</span>\n"
            html += "          </div>\n"
        html += "        </div>\n"
    
    html += """      </div>
    <div id="network">
      <h2 class="div_head">Network</h2>
      <div id="subnet">
        <span>Subnet</span> 
        <input type="text"/ name="subnet">
      </div>
      <div id="kavlan">
        <span>KaVLAN</span> 
        <input type="checkbox"/ name="kavlan">
      </div>
    </div>
    <div id="job_options">
      <h2 class="div_head">Job options</h2>
      <div id="job_name">
        <span>Name</span> 
        <input type="text" name="name"/>
      </div>
      <div id="submission">
        <span>Submission options</span> 
        <input type="text" name="submission_opts"/>
      </div>
    </div>
    <div id="submit_form">
      <input type="submit"/>
    </div>
    </form>    
  </div>
</body>
  <link rel="stylesheet" type="text/css" href="static/jquery.datetimepicker.css">
  <link rel="stylesheet" type="text/css" href="static/gray/easyui.css">
  <link rel="stylesheet" type="text/css" href="static/icon.css">
  <script src="static/jquery.js"></script>
  <script src="static/jquery.easyui.min.js"></script>
  <script src="static/jquery.datetimepicker.js"></script>
  <script src="static/jquery.timespinner.js"></script>
  <script>
    jQuery('#start_date_picker').datetimepicker({
      minDate: 0,
      step: 5
    });
    jQuery('#end_date_picker').datetimepicker({
      step: 5
    });
  </script>
  
</html>"""
    print html


if __name__=="__main__":
    print_header()
    if get_all_form_values() is None:
        print_form()
    else:
        print 'Your name is ',get_form_value()
#     print_footer()




exit()



# HEADER PAGE
    



print html
