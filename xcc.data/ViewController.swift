//  Created by {author_name} on {date}.
//  Copyright © {copyright_date} {copyright_name}. All rights reserved.
//

import UIKit

class {vc_name}: UIViewController {

    private let viewModel: {vm_name}

    // MARK: - Initialization

    init(viewModel: {vm_name}) {
        self.viewModel = viewModel
        super.init(nibName: nil, bundle: nil)
        view = {view_name}()

        updateView()
    }

    required init?(coder aDecoder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - Helper functions

    private func updateView() {
        guard let view = view as? {view_name} else {
            assertionFailure("View not of type {view_name}")
            return
        }
    }
}
