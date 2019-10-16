require([
    'jquery',
    'underscore',
    'splunkjs/mvc',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/simplexml/ready!',
], function($, _, mvc, TableView) {
    var DataBarCellRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return (cell.field === 'proportion');
        },
        render: function($td, cell) {
            $td.addClass('data-bar-cell').html(_.template('<div class="data-bar-wrapper"><div class="data-bar" style="width:<%- percent %>%"></div></div>', {
                percent: Math.min(Math.max(parseFloat(cell.value), 0), 100)
            }));
        }
    });

    var CustomHighlightRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return cell.field === 'orig_text';
        },
        render: function($td, cell) {
            var specificWord = defaultTokenModel.get("specific_word");
            var pattern = new RegExp("(\\b"+specificWord+")", "gi");
            var message = cell.value.replace(pattern, "<mark>$1</mark>")
            console.log(pattern);
            $td.html(_.template('<%= message%>', {
                message: message
            }));
        }
    });

    mvc.Components.get('tabledatabar').getVisualization(function(tableView) {
        tableView.addCellRenderer(new DataBarCellRenderer());
    });

    var defaultTokenModel = mvc.Components.get("default");
    mvc.Components.get('highlight').getVisualization(function(tableView) {
        tableView.on('rendered', function() {
            tableView.table.addCellRenderer(new CustomHighlightRenderer());
            tableView.table.render();
        });
    });
});
