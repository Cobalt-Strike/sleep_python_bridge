// dimensions
var width = 1000;
var height = 1000;

var margin = {
    top: 250,
    bottom: 50,
    left: 150,
    right: 50,
}

// create an svg to draw in
var svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    //.append('g')
    
    //.attr('transform', 'translate(' + margin.top + ',' + margin.left + ')');
    


    width = width - margin.left - margin.right;
    height = height - margin.top - margin.bottom;

// define marker
svg.append("svg:defs").selectAll("marker")
    .data(["arrow"])
  .enter().append("svg:marker")
    .attr("id", String)
    .attr("viewBox", "-0 -5 10 10")
    .attr("refX", 25)
    .attr("refY", 0)
    .attr("markerWidth", 13)
    .attr("markerHeight", 13)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M 0,-5 L 10 ,0 L 0,5");

// Define the div for the tooltip
var div = d3.select("body").append("div")	
    .attr("class", "tooltip")				
    .style("opacity", 0);

// Force settings
var simulation = d3.forceSimulation()
    // pull nodes together based on the links between them
    .force("link", d3.forceLink().id(function(d) {
        return d.id;
    })
    .strength(0.025))
    // push nodes apart to space them out
    .force("charge", d3.forceManyBody().strength(-200))
    // add some collision detection so they don't overlap
    .force("collide", d3.forceCollide().radius(12))
    // and draw them around the centre of the space
    .force("center", d3.forceCenter(width / 2, height / 2));
    
// load the graph
d3.json("data/beacons.json", function(error, graph) {
    // set the nodes
    var nodes = graph.nodes;
    // links between nodes
    var links = graph.links;

    
    // add the curved links to our graphic
    var link = svg.selectAll(".link")
        .data(links)
        .enter()
        .append("path")
        .attr("class", "link")
        // .attr('stroke', function(d){
        //     return "red";
        // })
        // Add arrows (styled with CSS)
        .attr("class", "link arrow")
        .attr("marker-end", "url(#arrow)");;
         
        link.append("title")
            .text(function (d) {return "d.type";});
        edgepaths = svg.selectAll(".edgepath")
            .data(links)
            .enter()
            .append('path')
            .attr('class', 'edgepath')
            .style("stroke",'orange')
            .attr('fill-opacity', 0)
            .attr('stroke-opacity', 0)
            .attr('id', function (d, i) {return 'edgepath' + i})
            .style("pointer-events", "none");

        // Link Label Settings
        edgelabels = svg.selectAll(".edgelabel")
            .data(links)
            .enter()
            .append('text')
            .style("pointer-events", "none")
            .attr('class', 'edgelabel')
            .attr('id', function (d, i) {return 'edgelabel' + i})
            .attr('font-size', 10)
            .attr('fill', 'orange');
        // Link Type Text
        edgelabels.append('textPath')
            .attr('xlink:href', function (d, i) {return '#edgepath' + i})
            .style("text-anchor", "middle")
            .style("pointer-events", "none")
            .attr("startOffset", "50%")
            .text(function (d) {
                return d.type
            });
        // TEST
        // asign a type per value to encode opacity


    // add the nodes to the graphic
    var node = svg.selectAll(".node")
        .data(nodes)
        .enter()
        .append("g")
        
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
        );
        //.on("end", dragended)

        
    // a circle to represent the node
    node.append("circle")
        .attr("class", "node")
        .attr("r", 20)
        .style("stroke", "green")
        .style("stroke-width", 2)
        .style("fill", "white")
        .style("fill-opacity",1);

    //Add Font Awesome (currently X)
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')


        //.text(function(d) { return '\uf118' })
        .text(function(d) { return d.nodeIcon })
        .style('font-family', 'FontAwesome')
        .style('font-size', '20px')
        .style('fill', 'red')
        .style("font-weight", 900)

        //.attr("stroke", function(d) {
        //    return d.colour;
        //})
        .on("mouseover", mouseOver(.2))
        .on("mouseout", mouseOut)
        ;

    // add a label to each node
    node.append("text")
        .attr("dx", 40) // Distance from node
        .attr("dy", ".35em") // Font size
        .text(function(d) {
            return d.user + "@" + d.host + " (" + d.pid + ")";
        })
        .style("stroke", "black")
        .style("stroke-width", 0.5)
        .style("fill", function(d) {
            return d.colour;
        });

    // add the nodes to the simulation and
    // tell it what to do on each tick
    simulation
        .nodes(nodes)
        .on("tick", ticked);

    // add the links to the simulation
    simulation
        .force("link")
        .links(links);

    // on each tick, update node and link positions
    function ticked() {
        link.attr("d", positionLink);
        node.attr("transform", positionNode);
        edgepaths.attr('d', function (d) {
            return 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y;
        });
        edgelabels.attr('transform', function (d) {
            if (d.target.x < d.source.x) {
                var bbox = this.getBBox();
                rx = bbox.x + bbox.width / 2;
                ry = bbox.y + bbox.height / 2;
                return 'rotate(180 ' + rx + ' ' + ry + ')';
            }
            else {
                return 'rotate(0)';
            }
        });
    }

    // links are drawn as curved paths between nodes,
    // through the intermediate nodes
    function positionLink(d) {
/*         var offset = 30;

        var midpoint_x = (d.source.x + d.target.x) / 2;
        var midpoint_y = (d.source.y + d.target.y) / 2;

        var dx = (d.target.x - d.source.x);
        var dy = (d.target.y - d.source.y);

        var normalise = Math.sqrt((dx * dx) + (dy * dy));

        var offSetX = midpoint_x + offset*(dy/normalise);
        var offSetY = midpoint_y - offset*(dx/normalise);

        return "M" + d.source.x + "," + d.source.y +
            "S" + offSetX + "," + offSetY +
            " " + d.target.x + "," + d.target.y; */

        // Link to itself reference http://jsfiddle.net/LUrKR/
        var x1 = d.source.x,
        y1 = d.source.y,
        x2 = d.target.x,
        y2 = d.target.y,
        dx = x2 - x1,
        dy = y2 - y1,
        dr = Math.sqrt(dx * dx + dy * dy),

        // Defaults for normal edge.
        drx = dr,
        dry = dr,
        xRotation = 30, // degrees
        largeArc = 0, // 1 or 0
        sweep = 0; // 1 or 0

        // Flip curves based on target / source X/Y coord relationship 
        if (d.target.y < d.source.y && d.target.x < d.source.x) {
            sweep = 1;
        } 
        if (d.target.y > d.source.y && d.target.x < d.source.x) {
            sweep = 0;
        } 
        if (d.target.y < d.source.y && d.target.x > d.source.x) {
            sweep = 0;
        } 
        if (d.target.y > d.source.y && d.target.x > d.source.x) {
            sweep = 1;
        } 
        
        // Self edge.
        if ( x1 === x2 && y1 === y2 ) {
            // Fiddle with this angle to get loop oriented.
            xRotation = -45;

            // Needs to be 1.
            largeArc = 1;

            // Change sweep to change orientation of loop. 
            //sweep = 0;

            // Make drx and dry different to get an ellipse
            // instead of a circle.
            drx = 10;
            dry = 75;
            
            // For whatever reason the arc collapses to a point if the beginning
            // and ending points of the arc are the same, so kludge it.
            x2 = x2 + 1;
            y2 = y2 + 1;
        } 
  
       return "M" + x1 + "," + y1 + "A" + drx + "," + dry + " " + xRotation + "," + largeArc + "," + sweep + " " + x2 + "," + y2;
            
    }

    // move the node based on forces calculations
    function positionNode(d) {
        // keep the node within the boundaries of the svg
        if (d.x < 0) {
            d.x = 0
        };
        if (d.y < 0) {
            d.y = 0
        };
        if (d.x > width) {
            d.x = width
        };
        if (d.y > height) {
            d.y = height
        };
        return "translate(" + d.x + "," + d.y + ")";
    }

    // build a dictionary of nodes that are linked
    var linkedByIndex = {};
    links.forEach(function(d) {
        linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });

    // check the dictionary to see if nodes are linked
    function isConnected(a, b) {
        return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
    }

    // fade nodes on hover
    function mouseOver(opacity) {
        return function(d) {
            // check all other nodes to see if they're connected
            // to this one. if so, keep the opacity at 1, otherwise
            // fade
            node.style("stroke-opacity", function(o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
            node.style("fill-opacity", function(o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
            // also style link accordingly
            link.style("stroke-opacity", function(o) {
                return o.source === d || o.target === d ? 1 : opacity;
            });
            link.style("stroke", function(o){
                return o.source === d || o.target === d ? o.source.colour : "#ddd";
            });

            // Show Popup 
            div.transition()        
                .duration(200)      
                .style("opacity", .9);      
            div .html("Beacon (" + d.id + ") Info" + "<hr/>" + 
                      "PID:  " + d.pid + "</br>" + 
                      "Host: " + d.host + "</br>" + 
                      "Computer: " + d.computer + "</br>" + 
                      "Int:  " + d.internal + "</br>" + 
                      "Ext:  " + d.external + "</br>" + 
                      "User: " + d.user + "</br>" + 
                      "OS:   " + d.os + " " + d.ver + "(" + d.barch + ")" + "</br>" + 
                      "Note: " + "</br>" + d.note 
        
        
                )  
                .style("left", (d3.event.pageX - 175) + "px")     // tooltip location
                .style("top", (d3.event.pageY - 175) + "px");     // tooltip location
                                




        };
    }

    function mouseOut() {
        node.style("stroke-opacity", 1);
        node.style("fill-opacity", 1);
        link.style("stroke-opacity", 1);
        link.style("stroke", "#ddd");
                  
        // Hide Popup
        div.transition()        
            .duration(500)      
            .style("opacity", 0);   
    }
    // Drag and move functions
    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x;
        d.fy = d.y;
    }
    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }
});