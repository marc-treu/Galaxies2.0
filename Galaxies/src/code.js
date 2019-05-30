$.getJSON("jsons/exemple.json", function (data) {
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data['elements'],
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(id)',
                    //'content': 'data(texte)',
                    'width': 'data(longueurTexte)',
		    'height' : 'data(longueurTexte)',
                    'background-color': function(node){ return 'rgb(0,'+(255-(node.degree()-1)*10)+',255)';},
                    'color': 'blue',
                    'background-fit': 'contain',
                    'background-clip': 'none'
                }
            },{
              selector: "node:selected",
              style: {
                'label': 'data(texte)',
                "border-width": "6px",
                "border-color": "#AAD8FF",
                "border-opacity": "0.5",
                "background-color": "#77828C",
                  "text-outline-color": "#77828C",
		  'text-background-color':'#ADFF2F',
		  'text-background-opacity':'0.8',
		  'text-background-shape': 'roundrectangle',
		  'text-background-padding': '3px',
		  'text-border-opacity': 1,
		  'text-border-width':'3px',
		  'text-border-style':'dashed',
		  'text-border-color':'#FF0000'
              }
            }, {
                selector: 'edge',
                style: {
                    'line-color': '#91b0ad',
                    'text-background-color': 'yellow',
                    'text-background-opacity': 0.4,
                    'width': '6px',
                    'target-arrow-shape': 'triangle',
                    'control-point-step-size': '140px'
                }
            }
        ],
        layout: {
            name: 'cose-bilkent',
	    nodeDimensionsIncludeLabels: true,
	    animate : false
	}
    });
  });

