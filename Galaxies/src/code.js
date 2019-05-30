$.getJSON("jsons/exemple.json", function (data) {
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data['elements'],
        style: [
            {
                selector: 'node',
                style: {
                    'label': function(node){ return GetLabel(node);},
                    'width': 'data(longueurTexte)',
		   			'height' : 'data(longueurTexte)',
                    'background-color': function(node){ return 'rgb(5,'+GetColor(node)+',5)';},
                    'color': 'blue',
                    'background-fit': 'contain',
                    'background-clip': 'none'
                }
            },{
              selector: "node:selected",
              style: {
                'label': function(node){showNodeInfo(node);},
                "border-width": "6px",
                "border-color": "#AAD8FF",
                "border-opacity": "0.5",
                "background-color": "#77828C",
                "text-outline-color": "#77828C",
              }
            },{
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

    function GetColor(node) { // Upgrade by using count as a global variable 
		var n, count = 0;
		for(n in Object.keys(data['elements']['edges'])) {
			count++;
		  }
    	return (count / node.degree()) * 255 / count;
    }
	
	function GetLabel(node){
		return node.data().texte.substring(0,15);
	}
	
	function showNodeInfo(node){
		Object.assign(node.data(), {'degre': node.degree()});
		console.log(node.data());
		var infoTemplate = Handlebars.compile([
			'<p>You have selecte the node number : {{id}}</p>',
			'<p>Which is connect to {{degre}} others nodes</p>',
			'<p>Came from : {{titre}}</p>',
			'<p>Written by : {{auteur}}</p>',
			'<p>In : {{date}}</p>',
			'<p>{{texte}}</p>',
		].join(''));
		console.log(infoTemplate);
		$('#info').html(infoTemplate(node.data())).show();
	}	
});


