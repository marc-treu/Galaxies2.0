$.getJSON("jsons/galaxie_9_amas_25.json", function (data) {
    var cy = cytoscape({
        container: document.getElementById('cy'),
        elements: data['elements'],
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(id)',
                    //'content': 'data(texte)',
                    'width': '60px',
                    'height': '60px',
                    'background-color': '#286990',
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
                "text-outline-color": "#77828C"
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
            name: 'circle'
        }
    });
  });
