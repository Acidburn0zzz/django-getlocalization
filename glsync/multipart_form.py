import itertools
import mimetools
import mimetypes

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.formFields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()

    def getContentType(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def addField(self, name, value):
        """Add a form field to the form data."""
        self.formFields.append((name, value))

    def addFile(self, fieldname, filename, fileHandle, mimetype=None):
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        self.files.append((fieldname, filename, mimetype, body))

    def __str__(self):
        parts = []
        partBoundary = '--' + self.boundary

        # Add the form fields

        parts.extend([ partBoundary,'Content-Disposition: form-data; name="%s"' % name,
        '', value,] for name, value in self.formFields)

        # Add the files to upload
        # Amazon S3 expects file data to be 'Content-Disposition:
        # form-data' instead of "file"

        parts.extend([ partBoundary,'Content-Disposition: form-data; name="%s"; filename="%s"' % \
        (fieldName, filename),'Content-Type: %s' % contentType,'',body,]
        for fieldName, filename, contentType, body in self.files)

        # Flatten the list and add closing boundary marker,
        # then return \r\n separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)
