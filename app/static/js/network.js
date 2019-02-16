$(function() {
    create_entity_network();
});

$( "#select_industry").change(function() {
    window.location.href = "/network/".concat($("#select_industry").val());
});

function clip(x, min, max){
    return Math.min(Math.max(x, min), max);
}

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

var color = d3.scaleLinear()
    .domain([-100, 0, 100])
    .range([d3.rgb(182,85,85), d3.rgb(201,185,125), d3.rgb(106,165,110)]);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.name;
    }))
    .force("charge", d3.forceManyBody()
        .strength(function (d) {
            return -400;
        }))
    .force("center", d3.forceCenter(width / 2, height / 2));

function create_entity_network() {
    // set the nodes
    var nodes = graph.nodes;
    // links between nodes
    var links = graph.links;

    //add encompassing group for the zoom
    var g = svg.append("g")
    .attr("class", "everything");

    var link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter()
        .append("line")
        .attr("class", function(d) {
            if (d.link_type === "ORGANIZATION"){
                return "organization";
            }else {
                return "person";
            }
        })
        .attr("stroke-width", function (d) {
            return d.weight;
        })
        .on("click", click_link);

    var node = g.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(graph.nodes)
        .enter().append("g");

    var circles = node.filter(function(d) {
            return d.type === "ORGANIZATION";
        })
        .append("circle")
        .attr("class", "organization")
        .attr("r", function (d) {
            return clip(40 * Math.sqrt(d.importance), 10, 30);
        })
        .attr("fill", function (d) {
            return color(d.sentiment_emb);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", mouseOver(.2))
        .on("mouseout", mouseOut)
        .on("click", click_node);

    var rectangle = node.filter(function (d) {
        return d.type === "PERSON";
    })
        .append("rect")
        .attr("class", "person")
        .attr("width", function (d) {
            return 1.5 * clip(40 * Math.sqrt(d.importance), 10, 30);
        })
        .attr("height", function (d) {
            return 1.5 * clip(40 * Math.sqrt(d.importance), 10, 30);
        })
        .attr("fill", function (d) {
            return color(d.sentiment_emb);
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", mouseOver(.2))
        .on("mouseout", mouseOut)
        .on("click", click_node);


    var lables = node
        .append("text")
        .attr("class", function(d) {
            if (d.type === "ORGANIZATION"){
                return "organization";
            }else {
                return "person";
            }
        })
        .text(function (d) {
            return d.name;
        })
        .attr('x', 12)
        .attr('y', 4);

    node.append("title")
        .text(function (d) {
            return d.name;
        });


    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    //add zoom capabilities
    var zoom_handler = d3.zoom()
        .on("zoom", zoom_actions);

    zoom_handler(svg);

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
    }

    // build a dictionary of nodes that are linked
    var linkedByIndex = {};
    links.forEach(function (d) {
        linkedByIndex[d.source.index + "," + d.target.index] = 1;
    });

    // check the dictionary to see if nodes are linked
    function isConnected(a, b) {
        return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
    }

    // fade nodes on hover
    function mouseOver(opacity) {
        return function (d) {
            // check all other nodes to see if they're connected
            // to this one. if so, keep the opacity at 1, otherwise
            // fade
            node.style("stroke-opacity", function (o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
            node.style("fill-opacity", function (o) {
                thisOpacity = isConnected(d, o) ? 1 : opacity;
                return thisOpacity;
            });
            // also style link accordingly
            link.style("stroke-opacity", function (o) {
                return o.source === d || o.target === d ? 1 : opacity;
            });
            // link.style("stroke", function (o) {
            //     return o.source === d || o.target === d ? o.source.colour : "#ddd";
            // });
        };
    }

    function mouseOut() {
        node.style("stroke-opacity", 1);
        node.style("fill-opacity", 1);
        link.style("stroke-opacity", 0.3);
        // link.style("stroke", "#ddd");
    }

    function click_node(d){
        var name = d.name;
        $.ajax({
            url: '/ajax_click_node',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'industry': industry,
                'name': name
            }),
            type: 'POST',
            success: function (response) {
                $("#section_news").html("");
                $("#section_news").hide();
                last_timestamp = "";
                var news = JSON.parse(response['news']);
                for (var i = 0; i < news.length; i++) {
                    var this_news = news[i];
                    $("#section_news").append(get_news_html(this_news,show_timeline=true));
                    enable_sentiment_override();
                }
                $("#section_news").slideDown(1000);
            }
        });
    }

    function click_link(d){
        var source = d.source.name;
        var target = d.target.name;
        $.ajax({
            url: '/ajax_click_link',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                'industry': industry,
                'source': source,
                'target': target
            }),
            type: 'POST',
            success: function (response) {
                $("#section_news").html("");
                $("#section_news").hide();
                last_timestamp = "";
                var news = JSON.parse(response['news']);
                for (var i = 0; i < news.length; i++) {
                    var this_news = news[i];
                    $("#section_news").append(get_news_html(this_news,show_timeline=true));
                    enable_sentiment_override();
                }
                $("#section_news").slideDown(1000);
            }
        });
    }

    //Zoom functions
    function zoom_actions(){
        g.attr("transform", d3.event.transform)
    }

    $("#toggle_person_button").click(function () {
        if($(this).attr('status') == "shown"){
            $("svg .person").hide(500);
            $(this).attr('status', "hidden");
            $(this).html("Show Person");
        }else{
            $("svg .person").show(500);
            $(this).attr('status', "shown") ;
            $(this).html("Hide Person");
        }
    })
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

