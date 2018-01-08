//  Created by {author_name} on {date}.
//  Copyright © {copyright_date} {copyright_name}. All rights reserved.
//

import XCTest
@testable import {project_name}

class {vm_name}Tests: XCTestCase {

    var sut: {vm_name}!

    override func setUp() {
        super.setUp()

        sut = {vm_name}()
    }

    func test_<#function name#>() {
        let expected = <#expected#>
        let result = sut.<#function name#>(<#properties#>)

        XCTAssertEqual(result, expected)
    }

}
