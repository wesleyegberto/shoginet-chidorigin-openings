(function () {
    var NOTATION_RE = /[▲▽△☗☖]/;

    function wrapMoveLines(td) {
        Array.from(td.childNodes).forEach(function (node) {
            if (node.nodeType !== Node.TEXT_NODE) return;
            var lines = node.textContent.split(/(<BR>|\n)/i);
            if (!lines.some(function (l) { return NOTATION_RE.test(l); })) return;
            var frag = document.createDocumentFragment();
            lines.forEach(function (line) {
                if (NOTATION_RE.test(line)) {
                    var code = document.createElement('code');
                    code.className = 'move-notation';
                    code.textContent = line;
                    frag.appendChild(code);
                } else {
                    frag.appendChild(document.createTextNode(line));
                }
            });
            td.replaceChild(frag, node);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('td[valign="top"]').forEach(wrapMoveLines);
    });
})();
