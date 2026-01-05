import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";
import { api } from "../../scripts/api.js"; // Import API to build image URLs

app.registerExtension({
    name: "ComfyUI.SimpleDisplay",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "SimpleDisplayNode") {

            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);

                // 1. Handle Text (Same as before)
                if (message && message.text) {
                    const w = this.widgets.find((w) => w.name === "displayed_text");
                    if (w) {
                        w.value = message.text[0];
                        // Intelligent Resizing
                        const lineCount = w.value.split("\n").length;
                        // Reserve extra height for the image (add 250px)
                        this.setSize([this.size[0], (lineCount * 20) + 300]);
                    }
                }

                // 2. Handle Images
                if (message && message.images) {
                    const imgData = message.images[0];
                    // Construct the URL to fetch the image from ComfyUI server
                    const url = api.apiURL(`/view?filename=${imgData.filename}&type=${imgData.type}&subfolder=${imgData.subfolder}`);

                    // Create an Image object in memory
                    const img = new Image();
                    img.src = url;

                    // When it loads, attach it to our node instance
                    img.onload = () => {
                        this.previewImage = img;
                        this.setDirtyCanvas(true); // Force re-draw
                    };
                }
            };

            // 3. Override the Draw Method
            // This runs 60 times a second to paint the node
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                onDrawForeground?.apply(this, arguments);

                // If we have an image loaded, draw it!
                if (this.previewImage) {
                    const padding = 10;
                    // Draw below the header
                    const y = 40;
                    const w = this.size[0] - (padding * 2);

                    // Calculate aspect ratio to fit nicely
                    const aspect = this.previewImage.width / this.previewImage.height;
                    const h = w / aspect;

                    // Draw the image
                    ctx.drawImage(this.previewImage, padding, y, w, h);

                    // Move the text widget down so it doesn't overlap the image
                    // (This is a visual hack, finding the widget and setting its Y position)
                    const textWidget = this.widgets.find(w => w.name === "displayed_text");
                    if (textWidget) {
                        textWidget.y = y + h + 20;
                    }
                }
            };
        }
    },
});