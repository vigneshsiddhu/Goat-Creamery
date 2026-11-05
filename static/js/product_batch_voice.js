document.addEventListener("DOMContentLoaded", function () {
    const rowsWrap = document.getElementById("voice-batch-rows");
    const batchCountInput = document.getElementById("batch-count");
    const mapEl = document.getElementById("product-recipe-map");
    const recipeLabel = document.getElementById("mapped-recipe");

    if (!rowsWrap || !batchCountInput) return;

    const recipeMap = mapEl ? JSON.parse(mapEl.textContent) : {};
    const milkMapEl = document.getElementById("milk-batch-map");
    const milkMap = milkMapEl ? JSON.parse(milkMapEl.textContent) : {};
    const wastagePill = document.getElementById("milk-wastage-pill");

    function rows() {
        return rowsWrap.querySelectorAll(".voice-batch-row");
    }

    function syncCheckoutState(row) {
        const checkout = row.querySelector(".voice-batch-checkout");
        row.classList.toggle("is-checked", Boolean(checkout && checkout.checked));
    }

    function renumberRows() {
        rows().forEach(function (row, index) {
            row.dataset.rowIndex = String(index);
            row.querySelectorAll("[name^='batch-']").forEach(function (el) {
                el.name = el.name.replace(/^batch-\d+-/, "batch-" + index + "-");
            });
            row.querySelectorAll("[id^='id_batch_']").forEach(function (el) {
                el.id = el.id.replace(/^id_batch_\d+_/, "id_batch_" + index + "_");
            });
            row.querySelectorAll("label[for^='id_batch_']").forEach(function (el) {
                el.htmlFor = el.htmlFor.replace(/^id_batch_\d+_/, "id_batch_" + index + "_");
            });
            const title = row.querySelector(".ingredient-form-section");
            if (title) title.textContent = index === 0 ? "Production batch" : "Milk batch " + (index + 1);
            const removeBtn = row.querySelector(".voice-batch-remove");
            if (removeBtn) removeBtn.hidden = index === 0;
            syncCheckoutState(row);
        });
        syncCopiedFields();
        batchCountInput.value = String(rows().length);
        renderRecipeList();
    }

    function firstRowValues() {
        const first = rows()[0];
        if (!first) return null;
        const product = first.querySelector(".voice-batch-product");
        const quantity = first.querySelector(".voice-batch-quantity");
        const unit = first.querySelector(".voice-batch-unit");
        const productText = product && product.selectedIndex >= 0 ? product.options[product.selectedIndex].text : "";
        return {
            product: product ? product.value : "",
            productText: productText,
            quantity: quantity ? quantity.value : "",
            unit: unit ? unit.value : "",
        };
    }

    function syncCopiedFields() {
        const values = firstRowValues();
        rows().forEach(function (row, index) {
            const summary = row.querySelector(".voice-copied-summary");
            if (index === 0) {
                row.classList.remove("is-extra");
                if (summary) {
                    summary.hidden = true;
                    summary.textContent = "";
                }
                return;
            }
            row.classList.add("is-extra");
            const product = row.querySelector(".voice-batch-product");
            const quantity = row.querySelector(".voice-batch-quantity");
            const unit = row.querySelector(".voice-batch-unit");
            if (values) {
                if (product) product.value = values.product;
                if (quantity) quantity.value = values.quantity;
                if (unit) unit.value = values.unit;
            }
            if (summary) {
                const parts = [];
                if (values && values.productText && values.product) parts.push(values.productText);
                if (values && values.quantity) parts.push(values.quantity + " " + (values.unit || ""));
                summary.textContent = parts.length ? "Using " + parts.join(" · ") : "Product and quantity copied from above";
                summary.hidden = false;
            }
        });
    }

    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function toGrams(quantity, unit) {
        const qty = parseFloat(quantity);
        if (!isFinite(qty) || qty <= 0) return 0;
        unit = (unit || "").toLowerCase();
        if (unit === "kg" || unit === "litre") return qty * 1000;
        if (unit === "gram" || unit === "ml") return qty;
        return 0;
    }

    function formatGrams(value) {
        if (!isFinite(value) || value <= 0) return "—";
        const rounded = Math.round(value * 10) / 10;
        return rounded.toLocaleString(undefined, { maximumFractionDigits: 1 }) + " g";
    }

    function rowScale(row, recipe) {
        const qtyInput = row.querySelector(".voice-batch-quantity");
        const unitInput = row.querySelector(".voice-batch-unit");
        const qty = parseFloat(qtyInput && qtyInput.value);
        if (!isFinite(qty) || qty <= 0) return 0;
        const unit = unitInput ? unitInput.value : "";
        const recipeWeight = parseFloat(recipe && recipe.weight);
        const enteredGrams = toGrams(qty, unit);
        if (recipeWeight > 0 && enteredGrams > 0) {
            return enteredGrams / recipeWeight;
        }
        return qty;
    }

    function selectedRecipes() {
        const first = rows()[0];
        if (!first) return [];
        const select = first.querySelector(".voice-batch-product");
        if (!select || !select.value) return [];
        const qtyInput = first.querySelector(".voice-batch-quantity");
        const unitInput = first.querySelector(".voice-batch-unit");
        return [{
            productLabel: select.options[select.selectedIndex] ? select.options[select.selectedIndex].text : "",
            recipe: recipeMap[select.value] || null,
            quantity: qtyInput ? qtyInput.value : "",
            unit: unitInput ? unitInput.value : "",
            scale: rowScale(first, recipeMap[select.value] || null),
        }];
    }

    function renderRecipeList() {
        const listEl = document.getElementById("product-recipe-list");
        const emptyEl = document.getElementById("product-recipe-empty");
        if (!listEl) return;

        const selected = selectedRecipes();
        if (!selected.length) {
            listEl.innerHTML = "";
            if (emptyEl) emptyEl.hidden = false;
            updateWastagePill();
            return;
        }

        if (emptyEl) emptyEl.hidden = true;
        listEl.innerHTML = selected.map(function (entry) {
            const recipe = entry.recipe;
            if (!recipe) {
                return (
                    '<article class="voice-recipe-card">' +
                    '<div class="voice-recipe-card-head"><h5>' + escapeHtml(entry.productLabel) + "</h5></div>" +
                    '<p class="voice-recipe-empty">No recipe mapped for this product.</p>' +
                    "</article>"
                );
            }
            const items = recipe.items || [];
            const scale = entry.scale;
            const batchLabel = entry.quantity
                ? escapeHtml(entry.quantity) + " " + escapeHtml(entry.unit || "")
                : "enter quantity";
            const itemsHtml = items.length
                ? '<ul class="voice-recipe-items">' + items.map(function (item) {
                    const baseGrams = parseFloat(item.grams);
                    const neededGrams = isFinite(baseGrams) && scale > 0 ? baseGrams * scale : 0;
                    return (
                        '<li class="voice-recipe-item">' +
                        '<div><span class="voice-recipe-item-name">' + escapeHtml(item.name) + "</span>" +
                        '<span class="voice-recipe-item-code">Recipe ' + escapeHtml(item.quantity) + " " + escapeHtml(item.unit) + "</span>" +
                        "</div>" +
                        '<div class="voice-recipe-item-qty"><strong>' + escapeHtml(formatGrams(neededGrams)) + "</strong></div>" +
                        "</li>"
                    );
                }).join("") + "</ul>"
                : '<p class="voice-recipe-empty">No ingredients in this recipe.</p>';
            return (
                '<article class="voice-recipe-card">' +
                '<div class="voice-recipe-card-head">' +
                "<h5>" + escapeHtml(recipe.product || entry.productLabel) + "</h5>" +
                '<div class="voice-recipe-meta">' +
                '<span class="voice-recipe-chip">Batch ' + batchLabel + "</span>" +
                '<span class="voice-recipe-chip">' + items.length + " ingredient" + (items.length === 1 ? "" : "s") + "</span>" +
                "</div></div>" +
                itemsHtml +
                "</article>"
            );
        }).join("");
        updateWastagePill();
    }

    function goatMilkUsedLitres(recipe, scale) {
        if (!recipe || !(scale > 0)) return 0;
        return (recipe.items || []).reduce(function (total, item) {
            if (!item.is_goat_milk) return total;
            const grams = parseFloat(item.grams);
            if (!isFinite(grams) || grams <= 0) return total;
            return total + (grams * scale) / 1000;
        }, 0);
    }

    function milkWastagePreview(milkId, used) {
        const milk = milkMap[milkId] || {};
        const previous = parseFloat(milk.wastage) || 0;
        const milkQty = parseFloat(milk.milk_quantity) || 0;
        const appended = previous + (used || 0);
        const remaining = milkQty - appended;
        if (remaining < 0) return 0;
        return Math.max(0, appended);
    }

    function updateWastagePill() {
        if (!wastagePill) return;
        const usedByMilk = {};
        rows().forEach(function (row) {
            const milkSelect = row.querySelector(".voice-batch-milk");
            const productSelect = row.querySelector(".voice-batch-product");
            if (!milkSelect || !milkSelect.value || !productSelect || !productSelect.value) return;
            const recipe = recipeMap[productSelect.value];
            if (!recipe) return;
            const milkId = milkSelect.value;
            usedByMilk[milkId] = (usedByMilk[milkId] || 0) + goatMilkUsedLitres(recipe, rowScale(row, recipe));
        });

        rows().forEach(function (row) {
            const milkSelect = row.querySelector(".voice-batch-milk");
            const hint = row.querySelector(".voice-milk-wastage");
            if (!hint || !milkSelect) return;
            const milkId = milkSelect.value;
            if (!milkId) {
                hint.hidden = true;
                hint.textContent = "Milk used 0.0 L";
                return;
            }
            const wastage = milkWastagePreview(milkId, usedByMilk[milkId] || 0);
            hint.textContent = "Milk used " + wastage.toFixed(2) + " L";
            hint.hidden = false;
        });

        const milkIds = Object.keys(usedByMilk);
        if (!milkIds.length) {
            wastagePill.textContent = "Milk used — select milk and quantity";
            wastagePill.classList.add("is-empty");
            wastagePill.classList.remove("is-warn");
            return;
        }
        const parts = [];
        let hasWastage = false;
        milkIds.forEach(function (milkId) {
            const milk = milkMap[milkId] || {};
            const wastage = milkWastagePreview(milkId, usedByMilk[milkId] || 0);
            if (wastage > 0) hasWastage = true;
            parts.push(wastage.toFixed(2) + " L");
        });
        wastagePill.textContent = "Milk used " + parts.join(" · ");
        wastagePill.classList.remove("is-empty");
        wastagePill.classList.toggle("is-warn", hasWastage);
    }

    function updateRecipeForSelect(select) {
        if (!recipeLabel || !select) return;
        const mapped = recipeMap[select.value];
        if (mapped) {
            recipeLabel.textContent = mapped.label;
            recipeLabel.classList.remove("is-empty", "is-warn");
        } else if (select.value) {
            recipeLabel.textContent = "No recipe for this product type";
            recipeLabel.classList.remove("is-empty");
            recipeLabel.classList.add("is-warn");
        } else {
            recipeLabel.textContent = "Recipe after product select";
            recipeLabel.classList.add("is-empty");
            recipeLabel.classList.remove("is-warn");
        }
        renderRecipeList();
    }

    function cloneRow(index) {
        const allRows = rows();
        const source = allRows[allRows.length - 1] || rowsWrap.querySelector(".voice-batch-row");
        if (!source) return null;
        const values = firstRowValues();
        const row = source.cloneNode(true);
        row.classList.add("is-extra");
        row.classList.remove("is-checked");
        row.dataset.rowIndex = String(index);
        row.querySelectorAll("[name^='batch-']").forEach(function (el) {
            el.name = el.name.replace(/^batch-\d+-/, "batch-" + index + "-");
            if (el.classList.contains("voice-batch-milk") || el.type === "checkbox") {
                if (el.type === "checkbox") el.checked = false;
                else el.selectedIndex = 0;
                return;
            }
            if (el.classList.contains("voice-batch-product") && values) {
                el.value = values.product;
                return;
            }
            if (el.classList.contains("voice-batch-quantity") && values) {
                el.value = values.quantity;
                return;
            }
            if (el.classList.contains("voice-batch-unit") && values) {
                el.value = values.unit;
            }
        });
        row.querySelectorAll("[id^='id_batch_']").forEach(function (el) {
            el.id = el.id.replace(/^id_batch_\d+_/, "id_batch_" + index + "_");
        });
        row.querySelectorAll("label[for^='id_batch_']").forEach(function (el) {
            el.htmlFor = el.htmlFor.replace(/^id_batch_\d+_/, "id_batch_" + index + "_");
        });
        row.querySelectorAll(".form-error").forEach(function (el) {
            el.remove();
        });
        const removeBtn = row.querySelector(".voice-batch-remove");
        if (removeBtn) removeBtn.hidden = false;
        return row;
    }

    function addRow() {
        const row = cloneRow(rows().length);
        if (!row) return;
        rowsWrap.appendChild(row);
        renumberRows();
        const milk = row.querySelector(".voice-batch-milk");
        if (milk) milk.focus();
        row.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    rowsWrap.addEventListener("input", function (event) {
        if (event.target.classList.contains("voice-batch-quantity")) {
            syncCopiedFields();
            renderRecipeList();
        }
    });

    rowsWrap.addEventListener("change", function (event) {
        if (event.target.classList.contains("voice-batch-product")) {
            syncCopiedFields();
            updateRecipeForSelect(event.target);
        }
        if (event.target.classList.contains("voice-batch-unit") || event.target.classList.contains("voice-batch-quantity") || event.target.classList.contains("voice-batch-milk")) {
            if (event.target.classList.contains("voice-batch-unit") || event.target.classList.contains("voice-batch-quantity")) {
                syncCopiedFields();
            }
            renderRecipeList();
        }
        if (event.target.classList.contains("voice-batch-checkout")) {
            const row = event.target.closest(".voice-batch-row");
            if (row) syncCheckoutState(row);
        }
    });

    rowsWrap.addEventListener("click", function (event) {
        const addBtn = event.target.closest(".voice-add-more-btn");
        if (addBtn) {
            event.preventDefault();
            addRow();
            return;
        }
        const removeBtn = event.target.closest(".voice-batch-remove");
        if (!removeBtn) return;
        const row = removeBtn.closest(".voice-batch-row");
        if (!row || row.dataset.rowIndex === "0") return;
        row.remove();
        renumberRows();
    });

    renumberRows();
    const firstProduct = rowsWrap.querySelector(".voice-batch-product");
    if (firstProduct) updateRecipeForSelect(firstProduct);
});
