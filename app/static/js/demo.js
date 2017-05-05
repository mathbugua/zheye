define(['jquery'], function() {
    (function () {
        var doc = $(document);
        var win = $(window);
        // 多次使用, 缓存起来
        doc.on('click', '.unfold', function () {
            var unfold = $(this);
            if (unfold.text() !== '收起') {
                unfold.text('收起').siblings('.part-content').hide().siblings('.all-content').show();
                var panel = unfold.parent();
                var panelScroll = panel.offset().top + panel.height();
                var scrollHeight = doc.scrollTop() + win.height();
                var right = win.width() / 2 - 350 + 20 > 20 ? win.width() / 2 - 350 + 20 : 20;
                if (scrollHeight - panelScroll < 50) {
                    unfold.addClass('fold-fix').css('right', right);
                }
                // scroll 事件性能优化
                // 鼠标滚动时 scroll 事件触发的间隔大约为 10~20 ms, 相对于其他的鼠标、键盘事件,它被触发的频率很高,间隔很近。
                // 如果 scroll 事件涉及大量的位置计算、元素重绘等工作,且这些工作无法在下个 scroll 事件触发前完成,就会导致浏览器掉帧
                // 1. 因此需要减少绑定给 scroll 中具体想要执行的业务逻辑的执行次数
                // 2. 并将对象初始化、不变的高度值等缓存在 scroll 事件外部
                // 存在 bug : 当以很快的速度滚动时,有可能执行不到 scroll 绑定的事件
                var cb = {
                    onscroll: function() {
                        var panelScroll = panel.offset().top + panel.height();
                        var scrollHeight = doc.scrollTop() + win.height();
                        var right = win.width() / 2 - 350 + 20 > 20 ? win.width() / 2 - 350 + 20 : 20;
                        if (scrollHeight - panelScroll < 50 &&
                            panel.offset().top - scrollHeight < -90 && unfold.text() !== '查看全部') {
                            unfold.addClass('fold-fix').css('right', right);
                        } else {
                            changeStyle(unfold);
                        }
                        win.off("scroll", cb.onscroll);
                        setTimeout(function() {
                            win.on("scroll", cb.onscroll);
                        }, 50);
                    }
                };
                win.on("scroll", cb.onscroll);

                // win.on('scroll', function () {
                //     var panelScroll = panel.offset().top + panel.height();
                //     var scrollHeight = doc.scrollTop() + win.height();
                //     if (scrollHeight - panelScroll < 50 &&
                //         panel.offset().top - scrollHeight < -90 && unfold.text() !== '展开') {
                //         unfold.addClass('fold-fix');
                //         unfold.css('right', right);
                //     } else {
                //         changeStyle(unfold);
                //     }
                // })

            } else {
                var fold = $(this);
                changeStyle(fold);
                fold.text('查看全部').siblings('.part-content').show()
                    .siblings('.all-content').hide();
            }
        });

        function changeStyle(i) {
            i.removeClass('fold-fix').css('right', '20px');
        }
    })()
});
